import uuid
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.agents.query_router import query_router
from app.satellite.catalog_client import catalog_client
from app.satellite.process_client import process_client
from app.agents.specialists import specialist_manager
from app.agents.evidence_agent import evidence_agent
from app.database.db import db_manager

router = APIRouter(prefix="/api/query", tags=["Natural Language Query Engine"])

class SatQueryRequest(BaseModel):
    query: str
    bbox: List[float]
    date_a: str
    date_b: str
    satellite_override: Optional[str] = "auto"
    location_label: Optional[str] = "Selected AOI Location"
    polygon_coords: Optional[List[List[float]]] = None

@router.post("/analyze")
def run_satquery_analysis(req: SatQueryRequest) -> Dict[str, Any]:
    """
    Main Earth Observation analysis workflow engine.
    Parses NL query, searches STAC Catalog for exact acquisition pass dates, retrieves real satellite imagery,
    runs specialist algorithms, and returns evidence.
    """
    if len(req.bbox) != 4:
        raise HTTPException(status_code=400, detail="bbox must be [min_lon, min_lat, max_lon, max_lat]")

    analysis_id = f"SQ-{uuid.uuid4().hex[:8].upper()}"

    # Step 1: Query Understanding & Routing
    query_info = query_router.parse_query(req.query)

    if req.satellite_override and req.satellite_override.lower() != "auto":
        query_info["primary_sensor"] = req.satellite_override.lower()

    satellite = query_info["primary_sensor"]

    # Step 2: Catalog Data Availability Search (Date A & Date B)
    cat_a = catalog_client.search_acquisitions(req.bbox, req.date_a, satellite=satellite)
    cat_b = catalog_client.search_acquisitions(req.bbox, req.date_b, satellite=satellite)

    act_date_a = cat_a.get("actual_date", req.date_a)
    act_date_b = cat_b.get("actual_date", req.date_b)

    # Use actual satellite pass ISO dates from STAC Catalog
    iso_a = cat_a.get("best_acquisition", {}).get("iso_date", req.date_a)
    iso_b = cat_b.get("best_acquisition", {}).get("iso_date", req.date_b)

    # Step 3: Fetch processed satellite imagery buffers from Copernicus Process API
    img_a_bytes, meta_a = process_client.fetch_image(
        bbox=req.bbox, date_iso=iso_a, satellite=satellite, evalscript_type="true_color"
    )
    img_b_bytes, meta_b = process_client.fetch_image(
        bbox=req.bbox, date_iso=iso_b, satellite=satellite, evalscript_type="true_color"
    )

    is_real = (not meta_a.get("is_fallback", False)) and (not meta_b.get("is_fallback", False))

    # Step 4: Run Specialist Pipeline
    specialist_res, change_map_bytes = specialist_manager.run_specialist_pipeline(
        specialist_name=query_info["specialist_agent"],
        bbox=req.bbox,
        date_a=req.date_a,
        date_b=req.date_b,
        img_a_bytes=img_a_bytes,
        img_b_bytes=img_b_bytes,
        is_real_data=is_real,
        cloud_a=cat_a.get("cloud_coverage", 4.0),
        cloud_b=cat_b.get("cloud_coverage", 5.0),
        gap_a=cat_a.get("temporal_gap_days", 0.0),
        gap_b=cat_b.get("temporal_gap_days", 1.0),
        polygon_coords=req.polygon_coords
    )

    # Step 5: Evidence Assembly
    evidence_pkg = evidence_agent.compile_evidence_package(
        query_info=query_info,
        specialist_res=specialist_res,
        catalog_a=cat_a,
        catalog_b=cat_b,
        img_a_bytes=img_a_bytes,
        img_b_bytes=img_b_bytes,
        change_map_bytes=change_map_bytes,
        bbox=req.bbox,
        date_a=req.date_a,
        date_b=req.date_b,
        is_real_data=is_real
    )

    response_payload = {
        "success": True,
        "analysis_id": analysis_id,
        "query": req.query,
        "location_label": req.location_label,
        "bbox": req.bbox,
        "requested_date_a": req.date_a,
        "requested_date_b": req.date_b,
        "actual_date_a": act_date_a,
        "actual_date_b": act_date_b,
        "satellite": satellite,
        "evidence": evidence_pkg
    }

    # Step 6: Persist in Database
    db_manager.save_analysis(
        analysis_id=analysis_id,
        query=req.query,
        specialist=query_info["intent_label"],
        location_label=req.location_label,
        bbox=req.bbox,
        date_a=req.date_a,
        date_b=req.date_b,
        actual_date_a=act_date_a,
        actual_date_b=act_date_b,
        satellite=satellite,
        change_percentage=specialist_res["change_metrics"]["change_percentage"],
        affected_area_sq_km=specialist_res["change_metrics"]["affected_area_sq_km"],
        earth_change_score=specialist_res["change_metrics"]["earth_change_score"],
        confidence_pct=specialist_res["confidence"]["overall_confidence_pct"],
        result_json=response_payload
    )

    return response_payload
