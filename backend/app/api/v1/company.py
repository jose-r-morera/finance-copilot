from typing import Any

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.core.database import get_session
from backend.app.models.company import Company, Competitor, FinancialStatement, StockPrice
from backend.app.services.ingestion import ingestion_manager
from backend.app.services.sec_insights import sec_insights_service

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/{ticker}/analysis")
async def get_company_analysis(
    ticker: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),  # noqa: B008
) -> dict:
    """
    Returns a consolidated analysis object for a company.
    Automatically triggers ingestion in background if data is missing.
    """
    try:
        logger.info("Fetching company analysis", ticker=ticker)

        # 1. Get Company Info
        company = session.exec(select(Company).where(Company.ticker == ticker)).first()
        if not company:
            logger.info("Company missing, triggering auto-ingestion", ticker=ticker)
            background_tasks.add_task(ingestion_manager.ingest_company_data, ticker)
            return {
                "status": "processing",
                "ticker": ticker,
                "message": (
                    f"Ingestion triggered for {ticker}. "
                    "Please wait while we fetch the latest data."
                ),
            }

        # Auto-fix missing logo if found (background)
        if not company.logo_url:
            logger.info("Company logo missing, triggering logo-only ingestion", ticker=ticker)
            background_tasks.add_task(ingestion_manager.ingest_company_data, ticker)

        # ... rest of the logic ...

        # 2. Get Financial Statements (ASC for chronological UI)
        financials = session.exec(
            select(FinancialStatement)
            .where(FinancialStatement.company_id == company.id)
            .order_by(FinancialStatement.fiscal_year)  # type: ignore[arg-type]
        ).all()

        # 3. Get Stock Price History
        prices = session.exec(
            select(StockPrice).where(StockPrice.company_id == company.id).order_by(StockPrice.date)  # type: ignore[arg-type]
        ).all()

        # 4. Get Competitors
        competitors_list: list[Any] = list(
            session.exec(select(Competitor).where(Competitor.company_id == company.id)).all()
        )

        # If no explicit competitors, find peers in same industry
        if not competitors_list:
            peers = session.exec(
                select(Company)
                .where(Company.industry == company.industry)
                .where(Company.id != company.id)
                .limit(5)
            ).all()
            competitors_list = [
                {"peer_ticker": p.ticker, "peer_name": p.name, "market_cap": p.market_cap}
                for p in peers
            ]

        # 5. Determine status based on ingest flag
        status = "ready" if company.is_ingested else "processing"

        # 6. Get SEC Insights (Postgres with RAG fallback)
        sec_insights = {"risk_factors": sec_insights_service.get_risk_factors(ticker, session)}

        return {
            "status": status,
            "company": company,
            "financials": financials,
            "prices": prices,
            "sec_insights": sec_insights,
            "competitors": competitors_list,
        }

    except Exception as e:
        logger.exception("Analysis endpoint failed", ticker=ticker, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/{ticker}/status")
def get_ingestion_status(ticker: str, session: Session = Depends(get_session)) -> dict:  # noqa: B008
    """
    Quick check to see if we have enough data to show an analysis.
    """
    company = session.exec(select(Company).where(Company.ticker == ticker)).first()
    if not company:
        return {"status": "missing"}

    # Check if we have financials
    has_financials = (
        session.exec(
            select(FinancialStatement).where(FinancialStatement.company_id == company.id)
        ).first()
        is not None
    )

    return {"status": "ready" if has_financials else "ingesting", "company_name": company.name}
