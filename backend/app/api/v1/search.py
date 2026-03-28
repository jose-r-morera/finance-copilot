
import structlog
from fastapi import APIRouter, HTTPException, Query

from ...services.sec_search import company_search_service

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/companies")
async def search_companies(
    q: str = Query(..., min_length=1, description="Search query for company name or ticker"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of results to return"),
) -> list[dict]:
    """
    Search for SEC-listed companies by name or ticker.
    Supports real-time autocomplete with ranked matching.
    """
    try:
        results = await company_search_service.search(q, limit=limit)
        return results
    except Exception as e:
        logger.error("Search endpoint failed", query=q, error=str(e))
        raise HTTPException(
            status_code=500, detail="Internal server error during search"
        ) from e
