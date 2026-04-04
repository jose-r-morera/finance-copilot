import httpx
import structlog

from backend.app.core.config import settings

logger = structlog.get_logger(__name__)


class CompanySearchService:
    """
    Service to manage and search the SEC's company ticker registry.
    Data is fetched from: https://www.sec.gov/files/company_tickers.json
    """

    _registry: list[dict] = []
    _is_initialized: bool = False

    @classmethod
    async def initialize(cls) -> None:
        """
        Fetch the company ticker registry from the SEC if not already loaded.
        In production, this would be cached in Redis with a 24h TTL.
        """
        if cls._is_initialized:
            return

        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {"User-Agent": settings.SEC_EDGAR_USER_AGENT}

        try:
            logger.info("Initializing SEC company registry", url=url)
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                # SEC JSON format:
                # { "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ... }
                cls._registry = [
                    {
                        "cik": str(v["cik_str"]).zfill(10),  # standard SEC CIK length
                        "ticker": v["ticker"],
                        "name": v["title"],
                    }
                    for v in data.values()
                ]
                cls._is_initialized = True
                logger.info(
                    "SEC company registry initialized successfully",
                    count=len(cls._registry),
                )
        except Exception as e:
            logger.error("Failed to initialize SEC company registry", error=str(e))
            # Fallback to empty registry to prevent app crash,
            # but log specifically as an infrastructure failure.
            cls._registry = []
            cls._is_initialized = False

    @classmethod
    async def search(cls, query: str, limit: int = 5) -> list[dict]:
        """
        Search for companies by ticker or name with ranked results.
        Priority:
        1. Ticker exact match
        2. Ticker prefix match
        3. Name prefix match
        4. Name contains query
        """
        if not query:
            return []

        if not cls._is_initialized:
            await cls.initialize()

        q = query.strip().lower()

        # Scoring/Ranking matches
        results = []
        for co in cls._registry:
            ticker = co["ticker"].lower()
            name = co["name"].lower()

            score = 0
            if ticker == q:
                score = 100
            elif ticker.startswith(q):
                score = 80
            elif name.startswith(q):
                score = 60
            elif q in name:
                score = 40

            if score > 0:
                results.append((score, co))

        # Sort by score descending and return top matches
        results.sort(key=lambda x: x[0], reverse=True)
        return [res[1] for res in results[:limit]]


# Singleton instance
company_search_service = CompanySearchService()
