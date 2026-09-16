from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.satellite.catalog_client import catalog_client

router = APIRouter(prefix="/api/satellite", tags=["Satellite Catalog"])

class AvailabilityCheckRequest(BaseModel):
    bbox: List[float]
    target_date: str
    satellite: str = "sentinel-2-l2a"
    max_cloud_cover: float = 30.0

@router.post("/availability")
def check_satellite_availability(req: AvailabilityCheckRequest) -> Dict[str, Any]:
    """
    Searches STAC Catalog API across ±3, ±7, ±15 day temporal windows to check data availability.
    """
    if len(req.bbox) != 4:
        raise HTTPException(status_code=400, detail="bbox must contain exactly 4 coordinates [min_lon, min_lat, max_lon, max_lat]")

    res = catalog_client.search_acquisitions(
        bbox=req.bbox,
        target_date=req.target_date,
        satellite=req.satellite,
        max_cloud_cover=req.max_cloud_cover
    )
    return res
