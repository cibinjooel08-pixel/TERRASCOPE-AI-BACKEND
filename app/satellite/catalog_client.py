import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from app.satellite.cdse_auth import cdse_auth

CATALOG_URL = os.getenv("SENTINEL_HUB_CATALOG_URL", "https://sh.dataspace.copernicus.eu/catalog/v1/search")

class CatalogClient:
    """
    Client for Copernicus STAC Catalog API (Sentinel-1 and Sentinel-2 acquisitions).
    """

    def search_acquisitions(
        self,
        bbox: List[float],
        target_date: str,
        satellite: str = "sentinel-2-l2a",
        max_cloud_cover: float = 30.0,
        window_days_list: List[int] = [3, 7, 15]
    ) -> Dict[str, Any]:
        """
        Search catalog using expanding temporal windows (±3, ±7, ±15 days) to find
        the best valid satellite acquisition.
        """
        try:
            target_dt = datetime.strptime(target_date[:10], "%Y-%m-%d")
        except ValueError:
            target_dt = datetime.utcnow()

        token, auth_info = cdse_auth.get_token()

        # If CDSE auth token is not available, return clear structured status
        if not token:
            return {
                "success": False,
                "status": auth_info.get("status", "UNCONFIGURED"),
                "error_code": auth_info.get("error_code", "AUTH_REQUIRED"),
                "message": auth_info.get("message", "Copernicus CDSE token unavailable."),
                "acquisitions": [],
                "best_acquisition": None
            }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Map user satellite selection to STAC collection
        collection = "sentinel-2-l2a"
        if "sentinel-1" in satellite.lower() or "sar" in satellite.lower():
            collection = "sentinel-1-grd"

        best_match = None
        searched_windows = []

        for window in window_days_list:
            start_dt = target_dt - timedelta(days=window)
            end_dt = target_dt + timedelta(days=window)

            time_range = f"{start_dt.strftime('%Y-%m-%dT00:00:00Z')}/{end_dt.strftime('%Y-%m-%dT23:59:59Z')}"

            payload = {
                "bbox": bbox,
                "datetime": time_range,
                "collections": [collection],
                "limit": 20
            }

            try:
                resp = requests.post(CATALOG_URL, json=payload, headers=headers, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    features = data.get("features", [])

                    valid_features = []
                    for f in features:
                        props = f.get("properties", {})
                        acq_date_str = props.get("datetime") or props.get("acquisitionDate")
                        if not acq_date_str:
                            continue
                        
                        try:
                            acq_dt = datetime.strptime(acq_date_str[:19], "%Y-%m-%dT%H:%M:%S")
                        except ValueError:
                            acq_dt = target_dt

                        diff_days = abs((acq_dt - target_dt).total_seconds()) / 86400.0
                        cloud_cover = props.get("eo:cloud_cover", 0.0) if collection == "sentinel-2-l2a" else 0.0

                        valid_features.append({
                            "id": f.get("id"),
                            "collection": collection,
                            "acquisition_date": acq_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "iso_date": acq_date_str,
                            "requested_date": target_dt.strftime("%Y-%m-%d"),
                            "diff_days": round(diff_days, 1),
                            "cloud_coverage": round(cloud_cover, 1),
                            "satellite": f.get("properties", {}).get("platform", "Sentinel"),
                            "bbox": f.get("bbox", bbox),
                            "geometry": f.get("geometry")
                        })

                    # Filter Sentinel-2 by cloud cover if possible
                    if collection == "sentinel-2-l2a":
                        filtered = [item for item in valid_features if item["cloud_coverage"] <= max_cloud_cover]
                        if not filtered and valid_features:
                            # fallback to lowest cloud cover feature if all exceed max
                            filtered = sorted(valid_features, key=lambda x: x["cloud_coverage"])
                        valid_features = filtered

                    if valid_features:
                        # Sort by combination of date proximity and low cloud cover
                        valid_features.sort(key=lambda x: (x["diff_days"], x["cloud_coverage"]))
                        best_match = valid_features[0]
                        searched_windows.append({"window_days": window, "found": len(valid_features)})
                        break
                    else:
                        searched_windows.append({"window_days": window, "found": 0})

            except requests.exceptions.RequestException as req_err:
                return {
                    "success": False,
                    "error_code": "CATALOG_API_TIMEOUT",
                    "message": f"Catalog API search failed: {str(req_err)}",
                    "searched_windows": searched_windows
                }

        if best_match:
            return {
                "success": True,
                "status": "AVAILABLE",
                "requested_date": target_dt.strftime("%Y-%m-%d"),
                "actual_date": best_match["acquisition_date"],
                "temporal_gap_days": best_match["diff_days"],
                "cloud_coverage": best_match["cloud_coverage"],
                "satellite": best_match["collection"],
                "best_acquisition": best_match,
                "searched_windows": searched_windows
            }
        else:
            return {
                "success": False,
                "status": "UNAVAILABLE",
                "error_code": "NO_SATELLITE_DATA",
                "message": f"No valid {collection} satellite acquisition found for target date {target_date} within ±15 days window.",
                "searched_windows": searched_windows,
                "suggestion": "Try choosing a different date range or increasing cloud tolerance."
            }

catalog_client = CatalogClient()
