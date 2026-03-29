from edgar import Company, set_identity
import structlog
import asyncio
from backend.app.core.config import settings
from backend.app.services.redis_service import redis_service

logger = structlog.get_logger(__name__)

# Set the identity for SEC EDGAR requests (mandatory)
set_identity(settings.SEC_EDGAR_USER_AGENT)

class SECIngestionService:
    """
    Service to fetch and parse SEC filings (10-K, 10-Q) using edgartools.
    Now with Redis caching.
    """

    @classmethod
    async def fetch_latest_filing(cls, ticker: str, filing_type: str = "10-K") -> str | None:
        """
        Fetch the text content of the latest filing of a specific type.
        Cached in Redis for 24h.
        """
        cache_key = f"sec:text:{ticker}:{filing_type}"
        cached = await redis_service.get(cache_key)
        if cached:
            logger.info("Serving SEC filing text from cache", ticker=ticker, type=filing_type)
            return cached

        try:
            logger.info("Fetching latest SEC filing", ticker=ticker, type=filing_type)
            company = await asyncio.to_thread(Company, ticker)
            filings = await asyncio.to_thread(company.get_filings, form=filing_type)
            
            if not filings:
                logger.warning("No filings found", ticker=ticker, type=filing_type)
                return None
            
            latest_filing = filings[0]
            logger.info("Found latest filing", ticker=ticker, accession_number=latest_filing.accession_number)
            
            text = await asyncio.to_thread(latest_filing.text)
            await redis_service.set(cache_key, text, expire=86400)
            return text
            
        except Exception as e:
            logger.error("Failed to fetch SEC filing", ticker=ticker, error=str(e))
            return None

    @classmethod
    async def get_filing_sections(cls, ticker: str, filing_type: str = "10-K", sections: list[str] | None = None) -> dict[str, str]:
        """
        Fetch specific sections from the latest filing.
        Cached in Redis for 24h.
        """
        if sections is None:
            sections = ["Item 1", "Item 1A", "Item 7"]
            
        cache_key = f"sec:sections:{ticker}:{filing_type}:{','.join(sections)}"
        cached = await redis_service.get(cache_key)
        if cached:
            logger.info("Serving SEC filing sections from cache", ticker=ticker, sections=sections)
            return cached

        try:
            logger.info("Fetching SEC filing sections from EDGAR", ticker=ticker, sections=sections)
            company = await asyncio.to_thread(Company, ticker)
            filings = await asyncio.to_thread(company.get_filings, form=filing_type)
            
            if not filings:
                return {}
            
            latest_filing = filings[0]
            doc = await asyncio.to_thread(latest_filing.obj)
            
            results = {}
            mapping = {
                "Item 1": "business",
                "Item 1A": "risk_factors",
                "Item 7": "management_discussion",
                "Business": "business",
                "Risk Factors": "risk_factors",
                "MD&A": "management_discussion"
            }
            
            for section_label in sections:
                attr_name = mapping.get(section_label)
                if attr_name and hasattr(doc, attr_name):
                    content = await asyncio.to_thread(getattr, doc, attr_name)
                    if content:
                        results[section_label] = str(content)
                else:
                    try:
                        section_content = await asyncio.to_thread(doc.get_section, section_label)
                        if section_content:
                            results[section_label] = str(section_content)
                    except Exception:
                        continue
            
            await redis_service.set(cache_key, results, expire=86400)
            return results
            
        except Exception as e:
            logger.error("Failed to fetch SEC filing sections", ticker=ticker, error=str(e))
            return {}

sec_ingestion_service = SECIngestionService()
