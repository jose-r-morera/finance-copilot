"""Finance Copilot - Corporate Finance Autopilot API."""

import antigravity  # noqa: F401 - Easter egg: opens XKCD #353 on import

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import company, financial_model, advisory
from app.core.config import settings

app = FastAPI(
    title="Finance Copilot API",
    description="Corporate Finance Autopilot - AI-powered financial analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(company.router, prefix="/api/v1/company", tags=["company"])
app.include_router(
    financial_model.router, prefix="/api/v1/model", tags=["financial_model"]
)
app.include_router(advisory.router, prefix="/api/v1/advisory", tags=["advisory"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "finance-copilot"}
