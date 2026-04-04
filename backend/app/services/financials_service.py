from datetime import datetime

import structlog
from sqlmodel import Session, select

from backend.app.core.database import engine
from backend.app.models.company import Company, FinancialStatement, StockPrice

logger = structlog.get_logger(__name__)


class FinancialsPersistenceService:
    """
    Service to handle the persistence of financial statements and stock prices in PostgreSQL.
    """

    @staticmethod
    def save_financials(company_ticker: str, financials: list[dict]) -> None:
        """
        Saves or updates financial statements for a company.
        """
        with Session(engine) as session:
            # 1. Get company id
            company = session.exec(select(Company).where(Company.ticker == company_ticker)).first()
            if not company:
                logger.error("Company not found for financials persistence", ticker=company_ticker)
                return

            for f_data in financials:
                # 2. Check if statement already exists for this year/period
                statement = session.exec(
                    select(FinancialStatement).where(
                        FinancialStatement.company_id == company.id,
                        FinancialStatement.fiscal_year == f_data["fiscal_year"],
                        FinancialStatement.period == f_data["period"],
                    )
                ).first()

                if statement:
                    # Update
                    for key, value in f_data.items():
                        setattr(statement, key, value)
                    statement.updated_at = datetime.utcnow()
                else:
                    # Create
                    new_statement = FinancialStatement(company_id=company.id, **f_data)
                    session.add(new_statement)

            session.commit()
            logger.info(
                "Saved financials to database", ticker=company_ticker, count=len(financials)
            )

    @staticmethod
    def save_stock_prices(company_ticker: str, prices: list[dict]) -> None:
        """
        Saves or updates historical stock prices.
        """
        with Session(engine) as session:
            company = session.exec(select(Company).where(Company.ticker == company_ticker)).first()
            if not company:
                return

            for p_data in prices:
                # Ensure date is a datetime object (it might be a string from Redis cache)
                date_val = p_data["date"]
                if isinstance(date_val, str):
                    date_val = datetime.strptime(date_val, "%Y-%m-%d")

                price_entry = session.exec(
                    select(StockPrice).where(
                        StockPrice.company_id == company.id, StockPrice.date == date_val
                    )
                ).first()

                if price_entry:
                    price_entry.close_price = p_data["close_price"]
                    price_entry.volume = p_data.get("volume")
                    price_entry.updated_at = datetime.utcnow()
                else:
                    new_price = StockPrice(
                        company_id=company.id,
                        date=date_val,
                        close_price=p_data["close_price"],
                        volume=p_data.get("volume"),
                    )
                    session.add(new_price)

            session.commit()
            logger.info("Saved stock prices to database", ticker=company_ticker, count=len(prices))


financials_persistence_service = FinancialsPersistenceService()
