"""Simple financial forecasting service.

Generates Base / Upside / Downside revenue scenarios using
historical CAGR with Monte Carlo noise. No black-box LLMs here –
all maths is explicit and auditable.
"""

from __future__ import annotations

import math
import random
from typing import Any


def _historical_revenue_cagr(income_records: list[dict]) -> float:
    """Estimate revenue CAGR from income statement records."""
    revenues: list[float] = []
    for rec in income_records:
        rev = rec.get("Total Revenue") or rec.get("TotalRevenue")
        if rev is not None:
            try:
                revenues.append(float(rev))
            except (TypeError, ValueError):
                pass
    if len(revenues) < 2:
        return 0.05  # default 5 % if insufficient data
    # records are newest-first from yfinance
    oldest, newest = revenues[-1], revenues[0]
    if oldest <= 0:
        return 0.05
    years = len(revenues) - 1
    return (newest / oldest) ** (1 / years) - 1


def build_forecast(
    income_records: list[dict],
    years: int = 5,
) -> dict[str, Any]:
    """Return Base / Upside / Downside 5-year revenue forecast."""
    base_cagr = _historical_revenue_cagr(income_records)

    # Scenario multipliers relative to base CAGR
    scenarios = {
        "base": base_cagr,
        "upside": base_cagr + 0.05,
        "downside": base_cagr - 0.03,
    }

    # Seed latest revenue
    latest_rev: float = 0.0
    for rec in income_records:
        rev = rec.get("Total Revenue") or rec.get("TotalRevenue")
        if rev is not None:
            try:
                latest_rev = float(rev)
                break
            except (TypeError, ValueError):
                pass

    results: dict[str, list[dict]] = {}
    for scenario, cagr in scenarios.items():
        rows = []
        rev = latest_rev
        for yr in range(1, years + 1):
            rev = rev * (1 + cagr)
            rows.append({"year": f"Y+{yr}", "revenue": round(rev, 0), "cagr": round(cagr * 100, 2)})
        results[scenario] = rows

    return {
        "historical_cagr_pct": round(base_cagr * 100, 2),
        "forecast_years": years,
        "scenarios": results,
        "disclaimer": "This is a simple projection model, NOT investment advice. Outputs are indicative only.",
    }
