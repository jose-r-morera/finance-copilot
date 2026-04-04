import json

import openai
import structlog
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlmodel import Session, select

from backend.app.core.config import settings
from backend.app.core.database import engine
from backend.app.models.company import Company, FinancialStatement, ForecastScenario
from backend.app.services.vector_store import vector_store_service

logger = structlog.get_logger(__name__)


class ModelingAgent:
    """
    Agent responsible for generating financial forecasts and DCF valuations.
    """

    def __init__(self) -> None:
        # Baseline assumptions (could be fetched from a macro service in the future)
        self.risk_free_rate = 0.042  # 4.2% (10Y Treasury)
        self.market_risk_premium = 0.055  # 5.5%
        self.default_terminal_growth = 0.02  # 2%

    async def generate_scenarios(self, ticker: str) -> list[ForecastScenario]:
        """
        Generates BASE, BULL, and BEAR scenarios for a company.
        """
        with Session(engine) as session:
            company = session.exec(select(Company).where(Company.ticker == ticker)).first()
            if not company:
                logger.error("Company not found for modeling", ticker=ticker)
                return []

            # 1. Fetch historical financials
            financials = session.exec(
                select(FinancialStatement)
                .where(FinancialStatement.company_id == company.id)
                .order_by(FinancialStatement.fiscal_year.desc())  # type: ignore
                .limit(4)
            ).all()

            if len(financials) < 2:
                logger.warning("Insufficient historical data for modeling", ticker=ticker)
                return []

            # 2. Calculate historical averages
            hist_metrics = self._calculate_historical_averages(financials)

            # 3. Fetch RAG Context (SEC Risk Factors & MD&A)
            rag_context = await self._fetch_rag_context(ticker)

            # 4. Generate AI-driven assumptions for 3 scenarios
            ai_assumptions = await self._get_ai_assumptions(company, hist_metrics, rag_context)

            # 5. Create scenarios using AI inputs
            scenarios = []
            for s_type in ["BASE", "BULL", "BEAR"]:
                data = ai_assumptions.get(s_type, {})
                scenario = self._create_scenario(
                    company,
                    hist_metrics,
                    s_type,
                    data.get("growth_mod", 0.0),
                    data.get("margin_mod", 0.0),
                    data.get("reasoning", ""),
                    data.get("thoughts", ""),
                    data.get("sources", []),
                    data.get("is_fallback", False),
                )

                # Perform DCF valuation
                self._calculate_dcf(scenario, company)

                scenarios.append(scenario)
                session.add(scenario)

            session.commit()
            for s in scenarios:
                session.refresh(s)

            logger.info("Generated 3 contextual scenarios for ticker", ticker=ticker)
            return scenarios

    async def _fetch_rag_context(self, ticker: str) -> dict:
        """
        Retrieves qualitative insights from ChromaDB with source metadata.
        """
        try:
            results = vector_store_service.query(
                query_texts=[
                    "fiscal outlook guidance growth margins risks opportunities capital allocation"
                ],
                n_results=10,
                where={"ticker": ticker},
            )
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]

            context_parts = []
            for doc, meta in zip(docs, metas, strict=False):
                source = meta.get("source_url", "SEC Filing")
                context_parts.append(f"Source: {source}\nContent: {doc}")

            return {
                "text": "\n---\n".join(context_parts)
                if context_parts
                else "No specific context found in filings.",
                "sources": list({m.get("source_url") for m in metas if m.get("source_url")}),
            }
        except Exception as e:
            logger.warning("RAG context fetch failed", ticker=ticker, error=str(e))
            return {"text": "Context unavailable.", "sources": []}

    async def _get_ai_assumptions(self, company: Company, hist: dict, context_data: dict) -> dict:
        """
        Uses an LLM to propose growth and margin modifiers based on RAG context with citations.
        """
        prompt = f"""
        Analyze the following financial data and qualitative context \
        for {company.name} ({company.ticker}).

        Historical Metrics:
        - Avg Revenue Growth: {hist['avg_growth']:.2%}
        - Avg EBITDA Margin: {hist['avg_margin']:.2%}

        Qualitative Context from SEC Filings (with Sources):
        {context_data['text']}

        Based on this data, propose growth and margin MODIFIERS for three scenarios.

        Return a JSON object with keys BASE, BULL, BEAR.
        Each should have:
        - growth_mod (float): e.g., 0.02 for +2%
        - margin_mod (float): e.g., -0.01 for -1%
        - reasoning (string): Concise explanation.
          IMPORTANT: You MUST cite the source URLs provided in the context for \
            any specific claims or guidance mentioned.
          Format citations as markdown links: [Source Name or Date](URL).
        - thoughts (string): A step-by-step summary of how you arrived at these numbers \
            (e.g., "Analyzed revenue CAGR of 15% and noted pressure on margins due to X...").
        - sources (list of strings): A list of the specific URLs used for this scenario.
        """

        try:
            # 1. Try Google Gemini if configured
            if settings.PRIMARY_LLM_PROVIDER == "google" and settings.GOOGLE_API_KEY:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=0.1,
                    convert_system_message_to_human=True,
                )
                # Gemini often works better with a direct prompt than
                # system/human split for structured JSON
                response = await llm.ainvoke(
                    [HumanMessage(content=prompt + "\n\nIMPORTANT: Return ONLY valid JSON.")]
                )
                return json.loads(response.content)

            # 2. Try OpenAI as default or explicit choice
            elif settings.OPENAI_API_KEY:
                client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                )
                return json.loads(response.choices[0].message.content)

            else:
                # Fallback to defaults
                raise ValueError("No LLM provider configured or keys missing.")
        except Exception as e:
            logger.error("LLM assumption generation failed, using defaults", error=str(e))
            source_url = (
                company.latest_filing_url or "https://www.sec.gov/edgar/searchedgar/companysearch"
            )
            source_link = f" ([Latest SEC Filing]({source_url}))"
            return {
                "BASE": {
                    "growth_mod": 0.0,
                    "margin_mod": 0.0,
                    "reasoning": f"Standard historical extrapolation \
                         based on past performance.{source_link}",
                    "thoughts": "Maintained status quo based on 4-year financial consistency.",
                    "sources": [source_url],
                    "is_fallback": True,
                },
                "BULL": {
                    "growth_mod": 0.02,
                    "margin_mod": 0.01,
                    "reasoning": f"Generic upside scenario assuming \
                        improved market conditions.{source_link}",
                    "thoughts": "Upside projection based on potential \
                         sector tailwinds and operational efficiency.",
                    "sources": [source_url],
                    "is_fallback": True,
                },
                "BEAR": {
                    "growth_mod": -0.03,
                    "margin_mod": -0.02,
                    "reasoning": f"Generic downside scenario based on sector \
                        risk factors.{source_link}",
                    "thoughts": "Downside risks primarily driven by macroeconomic \
                        volatility and margin compression.",
                    "sources": [source_url],
                    "is_fallback": True,
                },
            }

    def _calculate_historical_averages(self, financials: list[FinancialStatement]) -> dict:
        """
        Derives average growth rates and margins from historical data.
        """
        # Modern to oldest
        revs = [f.revenue for f in financials if f.revenue is not None]

        ebitdas = []
        for f in financials:
            # Safely handle all_metrics being None and revenue being None
            m = f.all_metrics if f.all_metrics is not None else {}
            rev = f.revenue if f.revenue is not None else 0.0
            ebitdas.append(m.get("ebitda") or (rev * 0.15))

        # Simple CAGR for Revenue
        if len(revs) >= 2:
            growth_rates = [(revs[i] / revs[i + 1]) - 1 for i in range(len(revs) - 1)]
            avg_growth = sum(growth_rates) / len(growth_rates)
        else:
            avg_growth = 0.05  # Default 5%

        # Average EBITDA Margin
        margins = [ebitdas[i] / revs[i] for i in range(len(revs)) if revs[i] > 0]
        avg_margin = sum(margins) / len(margins) if margins else 0.15

        # Average Tax Rate (Simulated or from data)
        avg_tax_rate = 0.21  # Default 21%

        last_rev = revs[0] if revs else 1e6

        return {
            "avg_growth": avg_growth,
            "avg_margin": avg_margin,
            "avg_tax_rate": avg_tax_rate,
            "last_revenue": last_rev,
            "last_year": financials[0].fiscal_year,
        }

    def _create_scenario(
        self,
        company: Company,
        hist: dict,
        s_type: str,
        g_mod: float,
        m_mod: float,
        reasoning: str = "",
        thoughts: str = "",
        sources: list[str] | None = None,
        is_fallback: bool = False,
    ) -> ForecastScenario:
        if sources is None:
            sources = []
        ForecastScenario(
            company_id=company.id,
            scenario_type=s_type,
            revenue_growth=hist["avg_growth"] + g_mod,
            ebitda_margin=hist["avg_margin"] + m_mod,
            terminal_growth=0.02,
            wacc=0.08,
            assumptions_reasoning=reasoning,
            modeling_thoughts=thoughts,
            data_sources=sources,
            is_fallback=is_fallback,
        )
        """
        Projects 5 years of financials based on modifiers.
        """
        growth = hist["avg_growth"] + g_mod
        margin = hist["avg_margin"] + m_mod

        projections = []
        curr_rev = hist["last_revenue"]

        for i in range(1, 6):
            year = hist["last_year"] + i
            curr_rev = curr_rev * (1 + growth)
            curr_ebitda = curr_rev * margin

            # Simple FCF Proxy = EBITDA * (1 - Tax) - CAPEX(3% rev) - NWC(1% rev)
            tax = curr_ebitda * hist["avg_tax_rate"]
            capex = curr_rev * 0.03
            nwc_change = curr_rev * 0.01
            fcf = curr_ebitda - tax - capex - nwc_change

            projections.append(
                {
                    "year": year,
                    "revenue": round(curr_rev, 2),
                    "ebitda": round(curr_ebitda, 2),
                    "fcf": round(fcf, 2),
                }
            )

        return ForecastScenario(
            company_id=company.id,
            scenario_type=s_type,
            revenue_growth=round(growth, 4),
            ebitda_margin=round(margin, 4),
            projections=projections,
            assumptions_reasoning=reasoning,
        )

    def _calculate_dcf(self, scenario: ForecastScenario, company: Company) -> None:
        """
        Calculates intrinsic value using DCF.
        """
        wacc = scenario.wacc
        g = scenario.terminal_growth

        # 1. Discount Projected FCFs
        pv_fcf = 0
        for i, proj in enumerate(scenario.projections):
            pv_fcf += proj["fcf"] / ((1 + wacc) ** (i + 1))

        # 2. Terminal Value (Gordon Growth)
        last_fcf = scenario.projections[-1]["fcf"]

        # Guard against wacc <= g
        denom = wacc - g
        if denom <= 0:
            logger.warning(
                "WACC <= Terminal Growth, adjusting spread for calculation", wacc=wacc, g=g
            )
            denom = 0.01  # Minimum spread to avoid explosion

        tv = (last_fcf * (1 + g)) / denom
        pv_tv = tv / ((1 + wacc) ** len(scenario.projections))

        # 3. Enterprise Value
        ev = pv_fcf + pv_tv

        # 4. Equity Value (Simplified: EV - Debt + Cash)
        # For a hackathon, we'll assume Net Debt is 0 if not explicitly in DB
        net_debt = 0  # Future: Fetch from Balance Sheet
        equity_value = ev - net_debt

        # 5. Intrinsic Value per share
        if company.shares_outstanding and company.shares_outstanding > 0:
            intrinsic_value = equity_value / company.shares_outstanding
        else:
            intrinsic_value = None

        scenario.enterprise_value = round(ev, 2)
        scenario.equity_value = round(equity_value, 2)
        scenario.intrinsic_value = round(intrinsic_value, 2) if intrinsic_value else None


modeling_agent = ModelingAgent()
