"""Unit tests for the forecasting service."""

import pytest
from app.services.forecasting import build_forecast, _historical_revenue_cagr


SAMPLE_INCOME = [
    {"Total Revenue": 100_000_000, "period": "2023"},
    {"Total Revenue": 90_000_000, "period": "2022"},
    {"Total Revenue": 81_000_000, "period": "2021"},
]


def test_cagr_calculation():
    cagr = _historical_revenue_cagr(SAMPLE_INCOME)
    # 81M -> 100M over 2 years: (100/81)^(1/2) - 1 ≈ 0.1111
    assert abs(cagr - 0.1111) < 0.001


def test_build_forecast_structure():
    result = build_forecast(SAMPLE_INCOME, years=3)
    assert "scenarios" in result
    assert set(result["scenarios"].keys()) == {"base", "upside", "downside"}
    for scenario in result["scenarios"].values():
        assert len(scenario) == 3
        for row in scenario:
            assert "year" in row
            assert "revenue" in row


def test_build_forecast_upside_gt_base():
    result = build_forecast(SAMPLE_INCOME, years=3)
    base_rev = result["scenarios"]["base"][-1]["revenue"]
    up_rev = result["scenarios"]["upside"][-1]["revenue"]
    assert up_rev > base_rev


def test_build_forecast_downside_lt_base():
    result = build_forecast(SAMPLE_INCOME, years=3)
    base_rev = result["scenarios"]["base"][-1]["revenue"]
    down_rev = result["scenarios"]["downside"][-1]["revenue"]
    assert down_rev < base_rev


def test_build_forecast_disclaimer():
    result = build_forecast(SAMPLE_INCOME)
    assert "disclaimer" in result
    assert "NOT investment advice" in result["disclaimer"]
