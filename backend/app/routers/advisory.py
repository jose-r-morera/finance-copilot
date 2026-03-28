"""AI-powered strategic advisory endpoint (Google Gemini)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.ai import get_gemini_response
from app.core.config import settings
from app.services.market_data import fetch_company_info, fetch_financials

router = APIRouter()


class AdvisoryRequest(BaseModel):
    ticker: str
    question: str = "What are the key funding and strategic options for this company?"


@router.post("/analyse")
async def analyse_company(req: AdvisoryRequest) -> dict:
    """Generate AI-powered strategic advisory using Gemini + live financial data."""
    info = fetch_company_info(req.ticker)
    if "error" in info:
        raise HTTPException(status_code=404, detail=info["error"])

    financials = fetch_financials(req.ticker)
    income = financials.get("income_statement", [])
    latest = income[0] if income else {}

    prompt = (
        f"You are a senior corporate finance advisor. "
        f"Company: {info.get('name')} ({req.ticker}), "
        f"Sector: {info.get('sector')}, "
        f"Market Cap: {info.get('market_cap')}, "
        f"Latest revenue: {latest.get('Total Revenue', 'N/A')}. "
        f"IMPORTANT: This is a student hackathon. Label any uncertainty clearly. "
        f"Do NOT present guesses as facts. Cite that all data is from public sources. "
        f"Question: {req.question}"
    )

    answer = get_gemini_response(prompt, api_key=settings.GOOGLE_API_KEY)
    return {
        "ticker": req.ticker,
        "company": info.get("name"),
        "question": req.question,
        "analysis": answer,
        "disclaimer": "NOT investment advice. Student hackathon output only.",
        "data_source": "Yahoo Finance public API",
    }
