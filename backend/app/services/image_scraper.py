import os
from io import BytesIO
from urllib.parse import urljoin

import httpx
import structlog
from bs4 import BeautifulSoup
from PIL import Image

logger = structlog.get_logger(__name__)


class ImageScraperService:
    @classmethod
    def download_and_save_logo(cls, ticker: str, logo_url: str) -> str | None:
        """
        Downloads a logo from a remote URL and saves it to the local static directory.
        Returns the local static path if successful.
        """
        if not logo_url or not ticker:
            return None

        try:
            # Ensure static directory exists
            # We use an absolute path relative to the file location to be safe
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            static_dir = os.path.join(base_dir, "static", "logos")
            os.makedirs(static_dir, exist_ok=True)

            file_path = os.path.join(static_dir, f"{ticker.upper()}.png")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            with httpx.Client(headers=headers, timeout=10.0, follow_redirects=True) as client:
                response = client.get(logo_url)
                response.raise_for_status()

                # Process image to ensure quality (crop, square, resize)
                processed_content = cls.process_image(response.content)
                if not processed_content:
                    logger.warning("Image processing failed, saving raw content", ticker=ticker)
                    processed_content = response.content

                assert processed_content is not None
                with open(file_path, "wb") as f:
                    f.write(processed_content)

            logger.info("Saved logo locally", ticker=ticker, path=file_path)
            # Return the path relative to the app's root /static mount
            return f"/static/logos/{ticker.upper()}.png"

        except Exception as e:
            logger.error(
                "Failed to download and save logo", ticker=ticker, url=logo_url, error=str(e)
            )
            return None

    @staticmethod
    def process_image(content: bytes) -> bytes | None:
        """
        Processes the image content with aggressive threshold-based trimming:
        1. Converts to grayscale and applies a threshold to ignore "almost white" background.
        2. Detects the bounding box of the actual logo content.
        3. Adds a 12% aesthetic margin around the logo.
        4. Squares and resizes to 512x512.
        """
        try:
            img = Image.open(BytesIO(content))

            # Ensure RGBA for transparency handling
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # 1. Aggressive Trim
            # Strategy: Convert to grayscale and threshold to isolate non-white content
            gray = img.convert("L")

            # Thresholding: pixels darker than 250 are considered "content"
            # This handles noisy or "almost white" backgrounds in metadata images
            thresh = gray.point(lambda p: 255 if p < 250 else 0)

            # Find bbox of thresholded content
            bbox_content = thresh.getbbox()

            # Also check for transparency channel strictly
            alpha = img.getchannel("A")
            bbox_alpha = alpha.getbbox()

            # Combine bboxes if both exist, otherwise use whichever is found
            if bbox_content and bbox_alpha:
                # Intersection or Union? Union is safer to not cut off parts of the logo
                bbox = (
                    min(bbox_content[0], bbox_alpha[0]),
                    min(bbox_content[1], bbox_alpha[1]),
                    max(bbox_content[2], bbox_alpha[2]),
                    max(bbox_content[3], bbox_alpha[3]),
                )
            elif bbox_content:
                bbox = bbox_content
            elif bbox_alpha:
                bbox = bbox_alpha
            else:
                bbox = None

            if bbox:
                # Add a tiny bit of context before cropping if possible (2px)
                bbox = (
                    max(0, bbox[0] - 2),
                    max(0, bbox[1] - 2),
                    min(img.width, bbox[2] + 2),
                    min(img.height, bbox[3] + 2),
                )
                img = img.crop(bbox)

            # 2. Add Aesthetic Padding (12.5%) and make square
            width, height = img.size
            # We want the logo to occupy roughly 75% of the final square
            padding_factor = 0.125

            max_dim = max(width, height)
            padding = int(max_dim * padding_factor)

            # Final canvas size before resizing
            new_size = max_dim + (2 * padding)

            # Create a transparent square canvas
            square_img = Image.new("RGBA", (new_size, new_size), (0, 0, 0, 0))

            # Center the cropped logo
            offset = ((new_size - width) // 2, (new_size - height) // 2)
            square_img.paste(img, offset)

            # 3. Final standard Resize
            final_img = square_img.resize((512, 512), Image.Resampling.LANCZOS)

            output = BytesIO()
            final_img.save(output, format="PNG", optimize=True)
            return output.getvalue()

        except Exception as e:
            logger.error("Failed to process image", error=str(e))
            return None

    @classmethod
    def get_logo_for_ticker(cls, ticker: str, website_url: str) -> str | None:
        """
        Main entry point. Iterates through multiple strategies to find a logo.
        Returns the local static path if successful.
        """
        if not website_url:
            return None

        # Clean URLs if they are just strings from yfinance
        if not website_url.startswith("http"):
            website_url = f"https://{website_url}"

        strategies = [
            # 1. DuckDuckGo Icons (High resolution icons service)
            lambda: cls.get_duckduckgo_icon_url(website_url),
            # 2. Meta Tags (og:image, apple-touch-icon)
            lambda: cls.scrape_metadata_logo(website_url),
            # 3. Clearbit API (Fallback)
            lambda: cls.get_clearbit_logo_url(website_url),
            # 4. Google Favicon (Last resort)
            lambda: cls.get_google_favicon_url(website_url),
        ]

        for strategy in strategies:
            remote_url = strategy()
            if remote_url:
                local_path = cls.download_and_save_logo(ticker, remote_url)
                if local_path:
                    logger.info(
                        "Logo ingestion successful",
                        ticker=ticker,
                        strategy=strategy.__name__ if hasattr(strategy, "__name__") else "lambda",
                    )
                    return local_path

        return None

    @staticmethod
    def get_duckduckgo_icon_url(website_url: str) -> str | None:
        """Constructs a DuckDuckGo icon URL from a website domain."""
        domain = website_url.replace("https://", "").replace("http://", "").split("/")[0]
        if domain:
            # DuckDuckGo's icon service is very reliable for high-quality square icons
            return f"https://icons.duckduckgo.com/ip3/{domain}.ico"
        return None

    @staticmethod
    def get_clearbit_logo_url(website_url: str) -> str | None:
        """Constructs a Clearbit logo URL from a website domain."""
        domain = website_url.replace("https://", "").replace("http://", "").split("/")[0]
        # Clean www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
        if domain:
            return f"https://logo.clearbit.com/{domain}"
        return None

    @staticmethod
    def get_google_favicon_url(website_url: str) -> str | None:
        """Constructs a Google Favicon URL."""
        domain = website_url.replace("https://", "").replace("http://", "").split("/")[0]
        if domain:
            return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
        return None

    @staticmethod
    def scrape_metadata_logo(website_url: str) -> str | None:
        """
        Scrapes a website for logo URLs in meta tags (og:image, apple-touch-icon).
        """
        try:
            logger.info("Attempting to scrape remote logo URL", url=website_url)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7",
            }

            with httpx.Client(headers=headers, timeout=10.0, follow_redirects=True) as client:
                response = client.get(website_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")

                    # 1. og:image
                    og_image = soup.find("meta", property="og:image")
                    if og_image and og_image.get("content"):
                        return urljoin(website_url, og_image["content"])

                    # 2. apple-touch-icon
                    apple_icon = soup.find("link", rel="apple-touch-icon")
                    if apple_icon and apple_icon.get("href"):
                        return urljoin(website_url, apple_icon["href"])

            # 5. Last Resort Scraping-style API (Google Favicon)
            domain = website_url.replace("https://", "").replace("http://", "").split("/")[0]
            if domain:
                return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"

            return None

        except Exception as e:
            logger.error("Failed to find remote logo", url=website_url, error=str(e))
            return None


image_scraper_service = ImageScraperService()
