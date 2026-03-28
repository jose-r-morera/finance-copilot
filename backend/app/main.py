from contextlib import asynccontextmanager
from fastapi import FastAPI

from .api.v1.router import router as api_router
from .core.database import init_db
from .core.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize logging and database
    setup_logging()
    init_db()
    yield
    # Shutdown: (No cleanup needed for now)

app = FastAPI(
    title="finance-copilot",
    description="Corporate Finance Autopilot",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to finance-copilot"}


app.include_router(api_router, prefix="/api/v1")
