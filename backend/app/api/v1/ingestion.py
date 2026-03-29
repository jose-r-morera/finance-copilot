from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import structlog
from backend.app.services.ingestion import ingestion_manager

logger = structlog.get_logger(__name__)
router = APIRouter()

class IngestionRequest(BaseModel):
    ticker: str
    filing_type: str = "10-K"

class IngestionResponse(BaseModel):
    status: str
    message: str | None = None
    ticker: str | None = None
    total_chunks: int | None = None

@router.post("/trigger", response_model=IngestionResponse)
async def trigger_ingestion(request: IngestionRequest, background_tasks: BackgroundTasks):
    """
    Triggers the ingestion of SEC filings for a company.
    Currently runs synchronously for simplicity, but can be moved to background.
    """
    logger.info("Ingestion request received", ticker=request.ticker, type=request.filing_type)
    
    # For now, let's run it synchronously to provide immediate feedback in logs/debug
    # In a real app, this should be a background task (see below).
    result = await ingestion_manager.ingest_company_data(request.ticker, request.filing_type)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return IngestionResponse(
        status="success",
        message="Ingestion completed successfully",
        ticker=result.get("ticker"),
        total_chunks=result.get("total_chunks")
    )

# Example of background trigger if needed:
# @router.post("/trigger-async")
# async def trigger_ingestion_async(request: IngestionRequest, background_tasks: BackgroundTasks):
#     background_tasks.add_task(ingestion_manager.ingest_company_data, request.ticker, request.filing_type)
#     return {"status": "accepted", "message": f"Ingestion for {request.ticker} started in background"}
