# WORKPLAN: finance-copilot

This workplan outlines the development of an agentic corporate finance autopilot. 
**Relational DB (PostgreSQL)**: Stores structured financials, company metadata, and saved forecast scenarios.
**Vector DB (Chroma)**: Stores embedded text from SEC filings and transcripts for Retrieval-Augmented Generation (RAG).

## Phase 1: Scaffolding & Relational Foundation (Day 0)
*Goal: Build the "skeleton" of the application — Infrastructure, Databases, and baseline UI.*

- [x] **Initial Project Structure**
    - [x] Create directory structure for Backend (FastAPI) and Frontend (Next.js).
    - [x] Initialize Git repository with proper `.gitignore`.
- [x] **CI/CD & Docker Setup (Backend, Redis)**
    - [x] Configure `docker-compose.yml` for local service orchestration.
    - [x] Setup **Backend** & **Frontend** services.
    - [x] Integrate **Redis** (used for agent state persistence and API caching).
- [x] **Add PostgreSQL to Docker & Config**
    - [x] Integrate **PostgreSQL** as the relational source of truth for financials.
    - [x] Setup persistent volumes and initial database schema.
- [x] **Add ChromaDB to Docker & Config (Chroma Setup)**
    - [x] Add **ChromaDB** to `docker-compose.yml` as our vector database for RAG.
    - [x] Configure `CHROMADB_HOST` and `CHROMADB_PORT` in environment.
- [x] **Environment Validation (Pydantic Settings)**
    - [x] Implement `pydantic-settings` for robust environment variable management.
    - [x] Validate critical API keys (OpenAI, SEC, Google) on startup.
- [x] **Agent Skills & Workflows (Stubs)**
    - [x] Create stubs for Ingestion, Modeling, and Advisory agents.
    - [x] Define base "Skills" and "Workflows" directory structure.
- [x] **Backend Health & Baseline (Functional)**
    - [x] Implement API Health Check endpoints.
    - [x] Verify backend connectivity to Redis and PostgreSQL.
- [x] **Logging & Error Handling (Basic structlog)**
    - [x] Setup **Structured Logging** (`structlog`) for JSON-based agent traces.
- [x] **Unit Tests for core API & baseline health**
    - [x] Implement unit tests for backend logic and DB connectivity.
- [x] **Frontend Minimalistic UI (React/Tailwind)**
    - [x] Implement premium Tailwind CSS theme and typography.
- [x] **UI Section Scaffolding (Brand, Competitors, Forecast, Advisory)**
    - [x] Scaffold Dashboard sections: Brand Positioning, Competitor Analysis, Forecast, Advisory.
- [x] **Legal: Financial Disclaimers & Non-Advice labels (UI Footer)**
    - [x] Implement legally mandatory disclaimers and educational purpose labels in the UI.

## Phase 2: Ingestion Agent & Vector Intelligence (Day 1 Morning)
*Goal: Populate databases with market data and searchable document chunks.*

- [x] **Ticker Identification & Meta-data enrichment**
    - [x] Develop service to map company names to stock tickers (e.g., "Apple" -> "AAPL").
- [ ] **SEC EDGAR & yfinance integration (Ingestion Agent)**
    - [ ] **Structured Fetch (yfinance)**: Fetch 5-year Income Statement, Balance Sheet, and Cash Flow.
    - [ ] **Unstructured Fetch (SEC EDGAR)**: Retrieve latest 10-K and 10-Q filing text.
- [ ] **Competitor Benchmarking (Peer tickers identification)**
    - [ ] Logic to automatically identify peer tickers and fetch their relative valuation multiples.
- [ ] **Brand & Positioning scraping engine (Logo, Mission, Key Facts)**
    - [ ] **Logo Retriever**: Automated retrieval of company logos.
    - [ ] **Scraping Engine**: Extract mission statements and strategic facts for the UI.
- [ ] **Data validation & PostgreSQL persistence layer**
    - [ ] Implement robust logic to save and validate financials in **PostgreSQL**.
    - [ ] Implement **Text Splitting & Embedding** for SEC filings; store results in **ChromaDB**.
- [ ] **Robust Error Handling (Retry logic for scrapers/APIs)**
    - [ ] Implement retry mechanisms and error boundaries for external scraping/API calls.
- [ ] **Redis Caching for API responses (yfinance/SEC)**
    - [ ] Enable caching to avoid rate limits and improve performance.
- [ ] **Integration Tests: Ingestion → Persistence → Cache flow**
    - [ ] End-to-end verification of the data pipeline.

## Phase 3: Reasoning & Modeling Agents (Day 1 Afternoon)
*Goal: The "Brain" phase — multi-agent choreography to generate forecasts and advice.*

- [ ] **Multi-agent "Director" (LangGraph + Redis)**
    - [ ] Central state manager to orchestrate the hand-offs between specialized agents.
- [ ] **Observability Integration (Langfuse + Traces)**
    - [ ] Log granular agentic reasoning steps and input/output tokens.
- [ ] **Modeling Agent: Multi-scenario Forecasting (Base, Upside, Downside)**
    - [ ] **Triple-Scenario Engine**: Predict Base, Bull (Upside), and Bear (Downside) cases.
    - [ ] **DCF Engine**: Calculate Intrinsic Value with WACC and terminal growth logic.
- [ ] **Sensitivity logic for key assumptions**
    - [ ] Test how valuation shifts with changes in growth or cost of capital.
- [ ] **Logic validation: Unit tests for financial formulas**
    - [ ] Verify the mathematical accuracy of DCF and projection calculations.
- [ ] **Advisory Agent: LLM-based reasoning for strategic options**
    - [ ] **RAG Implementation**: Search **ChromaDB** for qualitative insights.
    - [ ] **Strategic Memo**: Synthesize numbers and RAG context into advice (Funding & Strategy).
    - [ ] **Uncertainty Labeling**: Add clear labels for low-confidence data and high-uncertainty forecasts.
- [ ] **Citations & Source Attribution**
    - [ ] Ensure all advisory claims are backed by specific citations from filings or financial data.

## Phase 4: Viz & Reports (Day 2)
*Goal: Professional visualization and final delivery preparation.*

- [ ] **Chart generation service (Plotly/Matplotlib)**
    - [ ] Implement dynamic interactive financial charts (Revenue, Margins, Valuation Scenarios).
- [ ] **Thinking Process UI Log (Visible agentic traces)**
    - [ ] Show real-time "agent heartbeat" and reasoning steps in the dashboard.
- [ ] **PDF/PPTX Export pipeline (Optional / if enough time)**
    - [ ] Create basic professional report generator for the analysis.
- [ ] **Final End-to-End Test (E2E Pipeline)**
    - [ ] Conduct full system verification across multiple industry segments.

## Deliverables Prep
- [ ] **Demo Video Recording**
    - [ ] Showcase running system and explain the internal "Why" and pipeline architecture.
- [ ] **README Documentation Finalization**
    - [ ] Include "How to Run", Architecture summary, limitations, and third-party data notes.
- [ ] **One-page write-up**
    - [ ] Document Problem, Approach, Trade-offs, and "Future Work" plan.
- [ ] **Prompt Documentation**
    - [ ] Collect and document valuable prompts used for agent reasoning and multi-step logic.

---

## 🚀 Optional: Production Cloud Deployment
- [ ] Implement [deployment_plan.md](deployment_plan.md) (Vercel + Render + Upstash).
