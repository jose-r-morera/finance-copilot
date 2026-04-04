import asyncio
from typing import Any

import pandas as pd
import structlog
import yfinance as yf

from backend.app.services.redis_service import redis_service

logger = structlog.get_logger(__name__)


class YFinanceService:
    """
    Service to fetch structured financial data and market statistics using yfinance.
    Now with Redis caching support.
    """

    @staticmethod
    def _clean_dict(d: dict) -> dict[str, Any]:
        """
        Replaces NaN values with None to ensure JSON serializability.
        """
        return {k: (None if pd.isna(v) else v) for k, v in d.items()}

    @classmethod
    async def get_company_info(cls, ticker: str) -> dict[str, Any]:
        """
        Fetch general company information and key statistics.
        Cached in Redis for 24h.
        """
        cache_key = f"yf:info:{ticker}"
        cached = await redis_service.get(cache_key)
        if cached:
            logger.info("Serving company info from cache", ticker=ticker)
            return cached

        try:
            logger.info("Fetching company info from yfinance", ticker=ticker)
            ticker_obj = yf.Ticker(ticker)
            info = await asyncio.to_thread(lambda: ticker_obj.info)

            raw_data = {
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "description": info.get("longBusinessSummary"),
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "logo_url": info.get("logo_url"),
                "website": info.get("website"),
            }
            cleaned = cls._clean_dict(raw_data)
            await redis_service.set(cache_key, cleaned, expire=86400)
            return cleaned
        except Exception as e:
            logger.error("Failed to fetch company info", ticker=ticker, error=str(e))
            return {}

    @classmethod
    async def get_financials(cls, ticker: str) -> list[dict[str, Any]]:
        """
        Fetch last 5 years of Income Statement, Balance Sheet, and Cash Flow.
        Cached in Redis for 24h.
        """
        cache_key = f"yf:financials:{ticker}"
        cached = await redis_service.get(cache_key)
        if cached:
            logger.info("Serving financials from cache", ticker=ticker)
            return cached

        try:
            logger.info("Fetching financials from yfinance", ticker=ticker)
            ticker_obj = yf.Ticker(ticker)

            # Annual DataFrames (Fetch in thread)
            income_stmt = await asyncio.to_thread(lambda: ticker_obj.financials)
            balance_sheet = await asyncio.to_thread(lambda: ticker_obj.balance_sheet)
            cash_flow = await asyncio.to_thread(lambda: ticker_obj.cashflow)

            if income_stmt.empty:
                return []

            # Combine by fiscal year
            years = income_stmt.columns
            combined_data = []

            def get_val(
                df: pd.DataFrame, labels: list[str], current_date: pd.Timestamp
            ) -> float | None:
                for label in labels:
                    if label in df.index and not pd.isna(df.loc[label, current_date]):  # type: ignore[index]
                        return float(df.loc[label, current_date])  # type: ignore[index, arg-type]
                return None

            for date in years:
                year_data = {
                    "fiscal_year": date.year,
                    "period": "FY",
                    "revenue": get_val(
                        income_stmt, ["Total Revenue", "Operating Revenue", "Revenue"], date
                    ),
                    "net_income": get_val(
                        income_stmt,
                        [
                            "Net Income",
                            "Net Income Common Stockholders",
                            "Net Income From Continuing Operation Net Minority Interest",
                        ],
                        date,
                    ),
                    "total_assets": get_val(balance_sheet, ["Total Assets"], date),
                    "total_liabilities": get_val(
                        balance_sheet,
                        ["Total Liabilities Net Minority Interest", "Total Liabilities"],
                        date,
                    ),
                    "operating_cash_flow": get_val(
                        cash_flow,
                        ["Operating Cash Flow", "Cash Flow From Operating Activities"],
                        date,
                    ),
                    "all_metrics": {
                        "income_statement": cls._clean_dict(income_stmt[date].to_dict()),
                        "balance_sheet": cls._clean_dict(balance_sheet[date].to_dict()),
                        "cash_flow": cls._clean_dict(cash_flow[date].to_dict()),
                    },
                }
                combined_data.append(year_data)

            await redis_service.set(cache_key, combined_data, expire=86400)
            return combined_data
        except Exception as e:
            logger.error("Failed to fetch financials", ticker=ticker, error=str(e))
            return []

    @classmethod
    async def get_historical_prices(
        cls, ticker: str, period: str = "5y", interval: str = "1mo"
    ) -> list[dict[str, Any]]:
        """
        Fetch historical stock price data.
        Cached in Redis for 1h.
        """
        cache_key = f"yf:prices:{ticker}:{period}:{interval}"
        cached = await redis_service.get(cache_key)
        if cached:
            logger.info("Serving historical prices from cache", ticker=ticker)
            return cached

        try:
            logger.info("Fetching historical prices from yfinance", ticker=ticker, period=period)
            ticker_obj = yf.Ticker(ticker)
            history = await asyncio.to_thread(ticker_obj.history, period=period, interval=interval)

            prices = []
            for date, row in history.iterrows():
                prices.append(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "close_price": float(row["Close"]),
                        "volume": float(row["Volume"]),
                    }
                )

            await redis_service.set(cache_key, prices, expire=3600)
            return prices
        except Exception as e:
            logger.error("Failed to fetch historical prices", ticker=ticker, error=str(e))
            return []


yfinance_service = YFinanceService()
