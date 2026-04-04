import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.v1.router import router as api_router
from .core.database import init_db
from .core.logging import setup_logging
from .services.sec_search import CompanySearchService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: Initialize logging, database, and search registry
    setup_logging()
    init_db()
    await CompanySearchService.initialize()
    yield
    # Shutdown: (No cleanup needed for now)


app = FastAPI(
    title="finance-copilot",
    description="Corporate Finance Autopilot",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for frontend accessibility (3000 -> 8000)
# Note: allow_origins cannot be ["*"] when allow_credentials is True
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to finance-copilot"}


# Mount static files for logos
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(api_router, prefix="/api/v1")
