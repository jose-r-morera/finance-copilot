"""
Main API router for version 1.
Aggregates sub-routers for different resources.
"""

from fastapi import APIRouter

from .health import router as health_router
from .search import router as search_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["system"])
router.include_router(search_router, prefix="/search", tags=["search"])
