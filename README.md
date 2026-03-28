# 💹 Finance Copilot

> Corporate Finance Autopilot — AI-powered financial analysis and strategic advisory.
> **Student hackathon project. NOT investment advice.**

## How to Run

### Prerequisites
- Docker & Docker Compose, **or** Python 3.12+ and Node.js 20+

### Option A — Docker Compose (recommended)

```bash
cp .env.example .env
# Optional: add your GOOGLE_API_KEY to .env for real AI analysis
docker compose up --build
```

Open http://localhost:3000 in your browser.

### Option B — Local development

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GOOGLE_API_KEY
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
# UI: http://localhost:3000
```

## Architecture

```
┌───────────────────────────────────────────────┐
│  Next.js Frontend (port 3000)                 │
│  • Company search → ticker lookup             │
│  • Price chart (Recharts)                     │
│  • Revenue forecast: Base / Upside / Downside │
│  • AI Advisory panel                          │
└─────────────────────┬─────────────────────────┘
                      │ HTTP / REST
┌─────────────────────▼─────────────────────────┐
│  FastAPI Backend (port 8000)                  │
│  Routers:                                     │
│    GET  /api/v1/company/info/{ticker}         │
│    GET  /api/v1/company/prices/{ticker}       │
│    GET  /api/v1/company/financials/{ticker}   │
│    GET  /api/v1/model/forecast/{ticker}       │
│    POST /api/v1/advisory/analyse              │
│                                               │
│  Services:                                    │
│    market_data  ← Yahoo Finance (yfinance)    │
│    forecasting  ← CAGR-based scenario model   │
│    AI           ← Google Gemini 1.5 Flash     │
└───────────────────────────────────────────────┘
```

**Pipeline:** `ingest (yfinance) → parse → validate (Pydantic) → forecast → AI enrichment → API response → visualise`

### Google Antigravity 🚀

This project includes [Python's `antigravity` Easter egg](https://xkcd.com/353/) (`import antigravity`) as a hat-tip to the joy of programming. Beyond the joke, the project uses **Google Gemini** (via `google-generativeai`) as the AI reasoning layer for strategic advisory.

### AI Layer

- **Model:** Google Gemini 1.5 Flash — fast, cheap, capable for text analysis
- **Usage:** Agentic prompt construction from live financial data → structured advisory
- **Graceful degradation:** Works without `GOOGLE_API_KEY` (returns clearly labelled stub response)
- **Safety:** All AI outputs carry explicit disclaimers; uncertainty is always labelled

### Financial Model

- Revenue CAGR computed from last 4 years of income statement data (Yahoo Finance)
- Three scenarios: **Base** (historical CAGR), **Upside** (+5 pp), **Downside** (−3 pp)
- All formulas are explicit Python — no black-box ML

## Limitations

- Data from Yahoo Finance public API — subject to rate limits and availability
- AI advisory is indicative only — LLMs can hallucinate; all outputs carry disclaimers
- No persistent database — data fetched live on each request
- Financial model is intentionally simple (CAGR extrapolation); a production model would use DCF

## Third-Party Data & API Notes

| Source | Usage | Notes |
|--------|-------|-------|
| Yahoo Finance (`yfinance`) | Price history, financials, company info | Public, no API key required |
| Google Gemini (`google-generativeai`) | AI advisory text generation | Requires `GOOGLE_API_KEY` |
| Python `antigravity` | Easter egg / fun | Opens [XKCD #353](https://xkcd.com/353/) |

## Libraries Used

- **FastAPI** — async Python web framework
- **yfinance** — Yahoo Finance data (Apache 2.0)
- **pandas / numpy** — data wrangling
- **google-generativeai** — Google Gemini AI
- **Next.js 14** — React framework
- **Recharts** — React chart library
- **Tailwind CSS** — utility-first CSS
- **Docker** — containerisation