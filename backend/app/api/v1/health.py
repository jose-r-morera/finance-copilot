from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlmodel import Session

from ...core.database import get_session
from ...services.vector_store import vector_store_service

router = APIRouter()


@router.get("")
async def health_check(session: Annotated[Session, Depends(get_session)]) -> dict[str, str]:
    db_status = "ok"
    chroma_status = "ok" if vector_store_service.heartbeat() else "error"
    try:
        # Simple query to check DB connectivity
        session.execute(text("SELECT 1")).one()
    except Exception:
        db_status = "error"

    return {"status": "ok", "version": "0.1.0", "database": db_status, "chroma": chroma_status}
