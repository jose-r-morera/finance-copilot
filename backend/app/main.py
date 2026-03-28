"""
Main entry point for the FastAPI application.
Initializes the app, mounts routers, and defines lifespan events.
"""

from fastapi import FastAPI

from .api.v1.router import router as api_router

app = FastAPI(
    title="finance-copilot",
    description="Corporate Finance Autopilot",
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to finance-copilot"}


app.include_router(api_router, prefix="/api/v1")
