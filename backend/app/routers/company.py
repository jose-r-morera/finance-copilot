"""Company data endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.market_data import (
    fetch_company_info,
    fetch_financials,
    fetch_historical_prices,
)

router = APIRouter()


@router.get("/info/{ticker}")
async def get_company_info(ticker: str) -> dict:
    """Get company profile and metadata for a given ticker."""
    data = fetch_company_info(ticker)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@router.get("/prices/{ticker}")
async def get_prices(
    ticker: str,
    period: str = Query(default="1y", description="Period: 1y, 2y, 5y, max"),
) -> list[dict]:
    """Get historical OHLCV price data."""
    return fetch_historical_prices(ticker, period=period)


@router.get("/financials/{ticker}")
async def get_financials(ticker: str) -> dict:
    """Get income statement, balance sheet, and cash flow data."""
    data = fetch_financials(ticker)
    if "error" in data:
        raise HTTPException(status_code=502, detail=data["error"])
    return data
