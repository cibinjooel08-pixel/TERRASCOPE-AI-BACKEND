from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.database.db import db_manager

router = APIRouter(prefix="/api/history", tags=["Analysis History"])

@router.get("")
def list_history(limit: int = 20, filter_type: Optional[str] = None) -> Dict[str, Any]:
    """Lists historical satellite analyses."""
    items = db_manager.get_recent_analyses(limit=limit, filter_type=filter_type)
    total_count = db_manager.get_total_analyses_count()
    return {
        "success": True,
        "count": len(items),
        "total_count": total_count,
        "analyses": items
    }

@router.get("/{analysis_id}")
def get_history_detail(analysis_id: str) -> Dict[str, Any]:
    """Retrieves full analysis record by ID for replay."""
    record = db_manager.get_analysis_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Analysis ID {analysis_id} not found.")
    return {
        "success": True,
        "record": record
    }
