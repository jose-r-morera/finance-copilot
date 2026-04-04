import pytest

from backend.app.agents.modeling_agent import ModelingAgent
from backend.app.models.company import Company, ForecastScenario


def test_dcf_calculation_math() -> None:
    """
    Verify the DCF math logic in isolation.
    """
    agent = ModelingAgent()
    company = Company(ticker="TEST", name="Test Co", shares_outstanding=100)

    # Mock projections for 1 year for simplicity
    projections = [{"year": 2025, "revenue": 1000, "ebitda": 200, "fcf": 100}]
    scenario = ForecastScenario(
        company_id=1,
        scenario_type="BASE",
        revenue_growth=0.05,
        ebitda_margin=0.2,
        projections=projections,
        wacc=0.10,
        terminal_growth=0.02,
    )

    # Calculate:
    # PV(FCF1) = 100 / 1.1 = 90.91
    # TV = 100 * 1.02 / (0.10 - 0.02) = 102 / 0.08 = 1275
    # PV(TV) = 1275 / 1.1 = 1159.09
    # EV = 90.91 + 1159.09 = 1250
    # Price = 1250 / 100 = 12.50

    agent._calculate_dcf(scenario, company)

    assert scenario.enterprise_value == 1250.0
    assert scenario.intrinsic_value == 12.50


def test_historical_averages() -> None:
    """
    Check if historical averages are calculated correctly from statements.
    """
    from backend.app.models.company import FinancialStatement

    agent = ModelingAgent()

    f1 = FinancialStatement(company_id=1, fiscal_year=2024, revenue=110, all_metrics={"ebitda": 22})
    f2 = FinancialStatement(company_id=1, fiscal_year=2023, revenue=100, all_metrics={"ebitda": 20})

    metrics = agent._calculate_historical_averages([f1, f2])

    assert metrics["avg_growth"] == pytest.approx(0.10)
    assert metrics["avg_margin"] == pytest.approx(0.20)
    assert metrics["last_revenue"] == 110
