from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ...core.database import get_session
from sqlalchemy import text

router = APIRouter()

@router.get("")
async def health_check(session: Session = Depends(get_session)) -> dict[str, str]:
    db_status = "ok"
    try:
        # Simple query to check DB connectivity
        session.exec(text("SELECT 1")).one()
    except Exception:
        db_status = "error"
        
    return {
        "status": "ok", 
        "version": "0.1.0",
        "database": db_status
    }
