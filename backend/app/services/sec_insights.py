import structlog
from sqlmodel import Session, select

from backend.app.models.company import Company
from backend.app.services.vector_store import vector_store_service

logger = structlog.get_logger(__name__)


class SECInsightsService:
    @staticmethod
    def get_risk_factors(ticker: str, session: Session) -> str:
        """
        Retrieves the most relevant risk factors from PostgreSQL (primary) or ChromaDB (secondary).
        """
        try:
            # 1. Try PostgreSQL first (most reliable)
            company = session.exec(select(Company).where(Company.ticker == ticker)).first()
            if company and company.risk_factors:
                logger.info("Retrieved risk factors from PostgreSQL", ticker=ticker)
                return company.risk_factors

            # 2. Fallback to ChromaDB RAG
            results = vector_store_service.query(
                query_texts=["What are the primary risk factors for this company?"],
                n_results=3,
                where={"ticker": ticker, "section": "Item 1A"},
            )

            if not results or not results["documents"] or not results["documents"][0]:
                return "No risk factors found. Please ensure ingestion is complete."

            return "\n\n".join(results["documents"][0])

        except Exception as e:
            logger.error("Failed to retrieve risk factors", ticker=ticker, error=str(e))
            return "Error retrieving insights."


sec_insights_service = SECInsightsService()
