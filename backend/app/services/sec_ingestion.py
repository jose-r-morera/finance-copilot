from edgar import Company, set_identity
import structlog
from backend.app.core.config import settings

logger = structlog.get_logger(__name__)

# Set the identity for SEC EDGAR requests (mandatory)
set_identity(settings.SEC_EDGAR_USER_AGENT)

class SECIngestionService:
    """
    Service to fetch and parse SEC filings (10-K, 10-Q) using edgartools.
    """

    @staticmethod
    def fetch_latest_filing(ticker: str, filing_type: str = "10-K") -> str | None:
        """
        Fetch the text content of the latest filing of a specific type.
        """
        try:
            logger.info("Fetching latest SEC filing", ticker=ticker, type=filing_type)
            company = Company(ticker)
            filings = company.get_filings(form=filing_type)
            
            if not filings:
                logger.warning("No filings found", ticker=ticker, type=filing_type)
                return None
            
            # Get the latest one
            latest_filing = filings[0]
            logger.info("Found latest filing", ticker=ticker, accession_number=latest_filing.accession_number)
            
            # Use edgartools' built-in text extraction if possible, or get the full text
            # For 10-Ks, we might want specific sections.
            # To keep it simple for now, we'll get the full document text.
            return latest_filing.text()
            
        except Exception as e:
            logger.error("Failed to fetch SEC filing", ticker=ticker, error=str(e))
            return None

    @staticmethod
    def get_filing_sections(ticker: str, filing_type: str = "10-K", sections: list[str] | None = None) -> dict[str, str]:
        """
        Fetch specific sections from the latest filing.
        Example labels: 'Item 1', 'Item 1A', 'Item 7'
        """
        if sections is None:
            sections = ["Item 1", "Item 1A", "Item 7"]
            
        try:
            logger.info("Fetching SEC filing sections", ticker=ticker, sections=sections)
            company = Company(ticker)
            filings = company.get_filings(form=filing_type)
            
            if not filings:
                return {}
            
            latest_filing = filings[0]
            doc = latest_filing.obj()
            
            results = {}
            
            # Use high-level attributes for common sections if available
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
                    content = getattr(doc, attr_name)
                    if content:
                        results[section_label] = str(content)
                else:
                    # Fallback to general get_section if attribute not found
                    try:
                        section_content = doc.get_section(section_label)
                        if section_content:
                            results[section_label] = str(section_content)
                    except Exception:
                        continue
            
            return results
            
        except Exception as e:
            logger.error("Failed to fetch SEC filing sections", ticker=ticker, error=str(e))
            return {}

sec_ingestion_service = SECIngestionService()
