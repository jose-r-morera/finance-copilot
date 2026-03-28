"""Market data service using yfinance (Yahoo Finance public API)."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_company_info(ticker: str) -> dict[str, Any]:
    """Fetch company profile and metadata from Yahoo Finance."""
    try:
        t = yf.Ticker(ticker.upper())
        info = t.info
        return {
            "ticker": ticker.upper(),
            "name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "description": info.get("longBusinessSummary", ""),
            "market_cap": info.get("marketCap"),
            "currency": info.get("currency", "USD"),
            "website": info.get("website", ""),
            "country": info.get("country", ""),
            "employees": info.get("fullTimeEmployees"),
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch company info for %s: %s", ticker, exc)
        return {"ticker": ticker.upper(), "error": str(exc)}


def fetch_historical_prices(
    ticker: str, period: str = "5y"
) -> list[dict[str, Any]]:
    """Fetch historical OHLCV data."""
    try:
        t = yf.Ticker(ticker.upper())
        hist = t.history(period=period)
        hist = hist.reset_index()
        records = []
        for _, row in hist.iterrows():
            records.append(
                {
                    "date": str(row["Date"].date()),
                    "open": round(float(row["Open"]), 4),
                    "high": round(float(row["High"]), 4),
                    "low": round(float(row["Low"]), 4),
                    "close": round(float(row["Close"]), 4),
                    "volume": int(row["Volume"]),
                }
            )
        return records
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch prices for %s: %s", ticker, exc)
        return []


def fetch_financials(ticker: str) -> dict[str, Any]:
    """Fetch income statement, balance sheet, and cash flow statement."""
    try:
        t = yf.Ticker(ticker.upper())

        def _df_to_records(df: pd.DataFrame) -> list[dict]:
            if df is None or df.empty:
                return []
            df = df.T.reset_index()
            df.columns = [str(c) for c in df.columns]
            df.rename(columns={"index": "period"}, inplace=True)
            records = df.to_dict(orient="records")
            for r in records:
                for k, v in r.items():
                    if pd.isna(v):
                        r[k] = None
                    elif hasattr(v, "item"):
                        r[k] = v.item()
                    else:
                        try:
                            r[k] = float(v)
                        except (TypeError, ValueError):
                            r[k] = str(v)
            return records

        return {
            "income_statement": _df_to_records(t.financials),
            "balance_sheet": _df_to_records(t.balance_sheet),
            "cash_flow": _df_to_records(t.cashflow),
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch financials for %s: %s", ticker, exc)
        return {"error": str(exc)}
