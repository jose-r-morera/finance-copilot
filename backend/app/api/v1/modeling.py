import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.agents.modeling_agent import modeling_agent
from backend.app.core.database import get_session
from backend.app.models.company import Company, ForecastScenario

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/{ticker}/forecast")
async def get_forecast(ticker: str, session: Session = Depends(get_session)) -> dict:  # noqa: B008
    """
    Returns the three forecast scenarios (BASE, BULL, BEAR) for a company.
    If not already generated, it triggers the Modeling Agent.
    """
    try:
        logger.info("Fetching forecast scenarios", ticker=ticker)

        # 1. Check if company exists and is ingested
        company = session.exec(select(Company).where(Company.ticker == ticker)).first()
        if not company or not company.is_ingested:
            logger.info(
                "Company not yet fully ingested, returning processing status", ticker=ticker
            )
            return {"status": "processing", "ticker": ticker, "scenarios": []}

        # 2. Check for existing scenarios
        scenarios = session.exec(
            select(ForecastScenario)
            .where(ForecastScenario.company_id == company.id)
            .order_by(ForecastScenario.scenario_type)
        ).all()

        # 3. If missing, trigger Modeling Agent
        if not scenarios:
            logger.info("Scenarios missing, triggering Modeling Agent", ticker=ticker)
            scenarios = await modeling_agent.generate_scenarios(ticker)

        if not scenarios:
            return {"status": "processing", "ticker": ticker, "scenarios": []}

        return {
            "status": "ready",
            "ticker": ticker,
            "scenarios": [s.model_dump() for s in scenarios],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Modeling endpoint failed", ticker=ticker, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error during modeling.") from e


@router.get("/{ticker}/sensitivity")
async def get_sensitivity(ticker: str, session: Session = Depends(get_session)) -> dict:  # noqa: B008
    """
    Calculates a sensitivity matrix for the BASE scenario valuation.
    """
    try:
        company = session.exec(select(Company).where(Company.ticker == ticker)).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        base_scenario = session.exec(
            select(ForecastScenario).where(
                ForecastScenario.company_id == company.id, ForecastScenario.scenario_type == "BASE"
            )
        ).first()

        if not base_scenario:
            # Try to generate if missing
            scenarios = await modeling_agent.generate_scenarios(ticker)
            base_scenario = next((s for s in scenarios if s.scenario_type == "BASE"), None)

        if not base_scenario:
            raise HTTPException(status_code=404, detail="BASE scenario not found.")

        # Generate sensitivity matrix (WACC vs Terminal Growth)
        wacc_range = [base_scenario.wacc - 0.01, base_scenario.wacc, base_scenario.wacc + 0.01]
        g_range = [
            base_scenario.terminal_growth - 0.005,
            base_scenario.terminal_growth,
            base_scenario.terminal_growth + 0.005,
        ]

        results = []
        for w in wacc_range:
            row = []
            for g in g_range:
                # Recalculate intrinsic value with modified parameters
                val = _recalc_intrinsic_only(base_scenario, company, w, g)
                row.append({"wacc": w, "growth": g, "value": val})
            results.append(row)

        return {
            "wacc_labels": [f"{round(w*100, 1)}%" for w in wacc_range],
            "growth_labels": [f"{round(g*100, 1)}%" for g in g_range],
            "matrix": results,
        }

    except Exception as e:
        logger.exception("Sensitivity calculation failed", ticker=ticker)
        raise HTTPException(status_code=500) from e


def _recalc_intrinsic_only(
    scenario: ForecastScenario, company: Company, wacc: float, g: float
) -> float:
    # Discount Projected FCFs
    pv_fcf = 0
    for i, proj in enumerate(scenario.projections):
        pv_fcf += proj["fcf"] / ((1 + wacc) ** (i + 1))

    # Terminal Value
    last_fcf = scenario.projections[-1]["fcf"]
    # Guard against denominator = 0 or negative
    denom = wacc - g
    if denom <= 0:
        denom = 0.001

    tv = (last_fcf * (1 + g)) / denom
    pv_tv = tv / ((1 + wacc) ** len(scenario.projections))

    ev = pv_fcf + pv_tv
    equity_val = ev  # simplified

    if company.shares_outstanding:
        return round(equity_val / company.shares_outstanding, 2)
    return round(equity_val / 1e9, 2)  # return B if no shares
