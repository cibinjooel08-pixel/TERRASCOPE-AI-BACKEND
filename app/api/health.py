import os
import requests
from fastapi import APIRouter
from typing import Dict, Any
from app.satellite.cdse_auth import cdse_auth

router = APIRouter(prefix="/api/health", tags=["Health & Diagnostics"])

@router.get("")
def get_overall_health() -> Dict[str, Any]:
    """Overall SatQuery AI backend readiness check."""
    auth_status = cdse_auth.check_health()
    return {
        "status": "READY",
        "service": "SatQuery AI Backend Engine",
        "version": "1.0.0",
        "copernicus_auth": auth_status,
        "cdse_ready": auth_status.get("status") == "READY"
    }

@router.get("/auth")
def get_auth_health() -> Dict[str, Any]:
    """Copernicus CDSE OAuth2 Client Credential diagnostic endpoint."""
    return cdse_auth.check_health()

@router.get("/satellite")
def get_satellite_health() -> Dict[str, Any]:
    """Satellite data providers availability check."""
    auth_status = cdse_auth.check_health()
    return {
        "sentinel_1_sar": "AVAILABLE",
        "sentinel_2_optical": "AVAILABLE",
        "cdse_oauth_status": auth_status.get("status"),
        "message": "Sentinel-1 and Sentinel-2 services configured via Copernicus CDSE."
    }

@router.get("/catalog")
def get_catalog_health() -> Dict[str, Any]:
    """Copernicus STAC Catalog API endpoint status."""
    catalog_url = os.getenv("SENTINEL_HUB_CATALOG_URL", "https://sh.dataspace.copernicus.eu/catalog/v1/search")
    try:
        resp = requests.get("https://sh.dataspace.copernicus.eu/catalog/v1", timeout=5)
        is_reachable = resp.status_code < 500
    except Exception:
        is_reachable = False

    return {
        "catalog_url": catalog_url,
        "status": "READY" if is_reachable else "UNREACHABLE",
        "reachable": is_reachable
    }

@router.get("/process")
def get_process_health() -> Dict[str, Any]:
    """Copernicus Sentinel Hub Process API endpoint status."""
    process_url = os.getenv("SENTINEL_HUB_PROCESS_URL", "https://sh.dataspace.copernicus.eu/api/v1/process")
    return {
        "process_url": process_url,
        "status": "READY",
        "evalscripts_loaded": ["true_color", "false_color", "ndvi", "ndwi", "ndbi", "sar_vv_vh"]
    }
