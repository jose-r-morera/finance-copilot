# WORKPLAN: finance-copilot

## Phase 1: Scaffolding & Foundational Pipeline (Day 0)
- [x] Initial Project Structure
- [x] CI/CD & Docker Setup (Backend, Redis)
- [x] Add **PostgreSQL** to Docker & Config.
- [x] **Environment Validation** (Pydantic Settings).
- [x] Agent Skills & Workflows (Stubs).
- [x] Backend Health & Baseline (Functional).
- [x] **Logging & Error Handling** (Basic structlog).
- [x] **Unit Tests** for core API & baseline health.
- [x] Frontend Minimalistic UI (React/Tailwind)
- [x] **UI Section Scaffolding** (Brand, Competitors, Forecast, Advisory).
- [x] **Legal: Financial Disclaimers & Non-Advice labels** (UI Footer).

## Phase 2: Ingestion Agent Development (Day 1 Morning)
- [ ] Ticker Identification & Meta-data enrichment.
- [ ] SEC EDGAR & yfinance integration (Ingestion Agent).
- [ ] **Competitor Benchmarking** (Peer tickers identification).
- [ ] **Brand & Positioning scraping engine** (Logo, Mission, Key Facts).
- [ ] **Data validation & PostgreSQL persistence layer**.
- [ ] **Robust Error Handling** (Retry logic for scrapers/APIs).
- [ ] **Redis Caching** for API responses (yfinance/SEC).
- [ ] **Integration Tests**: Ingestion → Persistence → Cache flow.

## Phase 3: Reasoning & Modeling Agents (Day 1 Afternoon)
- [ ] **Multi-agent "Director" (LangGraph + Redis)**: Centrally manages Ingestion/Modeling/Advisory state.
- [ ] **Observability Integration** (Langfuse + Traces).
- [ ] **Modeling Agent**: Multi-scenario Forecasting (Base, Upside, Downside).
- [ ] Sensitivity logic for key assumptions.
- [ ] **Logic validation**: Unit tests for financial formulas.
- [ ] **Advisory Agent**: LLM-based reasoning for strategic options.
- [ ] **Citations & Uncertainty Labeling** (Link findings to sources).

## Phase 4: Viz & Reports (Day 2)
- [ ] Chart generation service (Plotly/Matplotlib).
- [ ] **Thinking Process UI Log** (Visible agentic traces).
- [ ] PDF/PPTX Export pipeline (Optional / if enough time).
- [ ] **Final End-to-End Test (E2E Pipeline)**.

## Deliverables Prep
- [ ] Demo Video Recording.
- [ ] README Documentation Finalization.
- [ ] One-page write-up.

---

## 🚀 Optional: Production Cloud Deployment
- [ ] Implement [deployment_plan.md](deployment_plan.md) (Vercel + Render + Upstash).
