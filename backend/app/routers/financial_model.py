"""Financial model and forecasting endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.market_data import fetch_financials
from app.services.forecasting import build_forecast

router = APIRouter()


@router.get("/forecast/{ticker}")
async def get_forecast(ticker: str, years: int = 5) -> dict:
    """Build Base / Upside / Downside revenue forecast for a ticker."""
    financials = fetch_financials(ticker)
    if "error" in financials:
        raise HTTPException(status_code=502, detail=financials["error"])
    income = financials.get("income_statement", [])
    return build_forecast(income, years=years)
