import yfinance as yf
import pandas as pd
import numpy as np
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger(__name__)

class YFinanceService:
    """
    Service to fetch structured financial data and market statistics using yfinance.
    """

    @staticmethod
    def _clean_dict(d: dict) -> dict:
        """
        Replaces NaN values with None to ensure JSON serializability.
        """
        return {k: (None if pd.isna(v) else v) for k, v in d.items()}

    @classmethod
    def get_company_info(cls, ticker: str) -> dict:
        """
        Fetch general company information and key statistics.
        """
        try:
            logger.info("Fetching company info from yfinance", ticker=ticker)
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            raw_data = {
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "description": info.get("longBusinessSummary"),
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "logo_url": info.get("logo_url")
            }
            return cls._clean_dict(raw_data)
        except Exception as e:
            logger.error("Failed to fetch company info", ticker=ticker, error=str(e))
            return {}

    @classmethod
    def get_financials(cls, ticker: str) -> list[dict]:
        """
        Fetch last 5 years of Income Statement, Balance Sheet, and Cash Flow.
        Returns a list of dictionaries, one per fiscal year.
        """
        try:
            logger.info("Fetching financials from yfinance", ticker=ticker)
            ticker_obj = yf.Ticker(ticker)
            
            # Annual DataFrames
            income_stmt = ticker_obj.financials  # Income Statement
            balance_sheet = ticker_obj.balance_sheet
            cash_flow = ticker_obj.cashflow
            
            if income_stmt.empty:
                return []

            # Combine by fiscal year
            years = income_stmt.columns
            combined_data = []
            
            for date in years:
                year_data = {
                    "fiscal_year": date.year,
                    "period": "FY",
                    "revenue": float(income_stmt.loc["Total Revenue", date]) if "Total Revenue" in income_stmt.index and not pd.isna(income_stmt.loc["Total Revenue", date]) else None,
                    "net_income": float(income_stmt.loc["Net Income", date]) if "Net Income" in income_stmt.index and not pd.isna(income_stmt.loc["Net Income", date]) else None,
                    "total_assets": float(balance_sheet.loc["Total Assets", date]) if "Total Assets" in balance_sheet.index and not pd.isna(balance_sheet.loc["Total Assets", date]) else None,
                    "total_liabilities": float(balance_sheet.loc["Total Liabilities Net Minority Interest", date]) if "Total Liabilities Net Minority Interest" in balance_sheet.index and not pd.isna(balance_sheet.loc["Total Liabilities Net Minority Interest", date]) else None,
                    "operating_cash_flow": float(cash_flow.loc["Operating Cash Flow", date]) if "Operating Cash Flow" in cash_flow.index and not pd.isna(cash_flow.loc["Operating Cash Flow", date]) else None,
                    "all_metrics": {
                        "income_statement": cls._clean_dict(income_stmt[date].to_dict()),
                        "balance_sheet": cls._clean_dict(balance_sheet[date].to_dict()),
                        "cash_flow": cls._clean_dict(cash_flow[date].to_dict())
                    }
                }
                combined_data.append(year_data)
                
            return combined_data
        except Exception as e:
            logger.error("Failed to fetch financials", ticker=ticker, error=str(e))
            return []

    @staticmethod
    def get_historical_prices(ticker: str, period: str = "5y", interval: str = "1mo") -> list[dict]:
        """
        Fetch historical stock price data.
        """
        try:
            logger.info("Fetching historical prices from yfinance", ticker=ticker, period=period)
            ticker_obj = yf.Ticker(ticker)
            history = ticker_obj.history(period=period, interval=interval)
            
            prices = []
            for date, row in history.iterrows():
                prices.append({
                    "date": date.to_pydatetime(),
                    "close_price": float(row["Close"]),
                    "volume": float(row["Volume"])
                })
            return prices
        except Exception as e:
            logger.error("Failed to fetch historical prices", ticker=ticker, error=str(e))
            return []

yfinance_service = YFinanceService()
