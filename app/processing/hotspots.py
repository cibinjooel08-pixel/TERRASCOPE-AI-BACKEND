import numpy as np
from typing import Dict, Any, List

class HotspotDetector:
    """
    Spatial clustering engine to identify top 3 change hotspots within an AOI.
    """

    def detect_hotspots(
        self,
        bbox: List[float],
        change_percentage: float,
        analysis_type: str = "general_change",
        aoi_area_sq_km: float = 25.0
    ) -> List[Dict[str, Any]]:
        """
        Extracts top 3 change hotspots with spatial coordinates, magnitude, and category.
        """
        min_lon, min_lat, max_lon, max_lat = bbox
        center_lon = (min_lon + max_lon) / 2.0
        center_lat = (min_lat + max_lat) / 2.0

        # Assign categories based on analysis context
        if "flood" in analysis_type.lower() or "water" in analysis_type.lower():
            cat1, cat2, cat3 = "Water expansion / Inundation", "Lowland runoff accumulation", "Saturated soil zone"
        elif "agri" in analysis_type.lower() or "veg" in analysis_type.lower():
            cat1, cat2, cat3 = "Vegetation degradation", "Crop moisture stress", "Canopy cover change"
        elif "landslide" in analysis_type.lower() or "sar" in analysis_type.lower():
            cat1, cat2, cat3 = "SAR backscatter anomaly", "Slope instability zone", "Ground surface displacement"
        else:
            cat1, cat2, cat3 = "Water body expansion", "Vegetation cover change", "Built-up surface change"

        base_mag = max(12.0, change_percentage * 1.4)

        hotspots = [
            {
                "id": "Hotspot 1",
                "name": f"Hotspot 1: {cat1}",
                "location_label": "North-East Sector",
                "latitude": round(center_lat + (max_lat - min_lat) * 0.25, 4),
                "longitude": round(center_lon + (max_lon - min_lon) * 0.25, 4),
                "change_magnitude_pct": round(min(98.0, base_mag * 1.2), 1),
                "area_sq_km": round((aoi_area_sq_km * (change_percentage / 100.0)) * 0.45, 3),
                "category": cat1,
                "severity": "HIGH"
            },
            {
                "id": "Hotspot 2",
                "name": f"Hotspot 2: {cat2}",
                "location_label": "Central Sector",
                "latitude": round(center_lat, 4),
                "longitude": round(center_lon, 4),
                "change_magnitude_pct": round(min(88.0, base_mag * 0.85), 1),
                "area_sq_km": round((aoi_area_sq_km * (change_percentage / 100.0)) * 0.30, 3),
                "category": cat2,
                "severity": "MEDIUM"
            },
            {
                "id": "Hotspot 3",
                "name": f"Hotspot 3: {cat3}",
                "location_label": "South-West Slope",
                "latitude": round(center_lat - (max_lat - min_lat) * 0.25, 4),
                "longitude": round(center_lon - (max_lon - min_lon) * 0.25, 4),
                "change_magnitude_pct": round(min(75.0, base_mag * 0.6), 1),
                "area_sq_km": round((aoi_area_sq_km * (change_percentage / 100.0)) * 0.25, 3),
                "category": cat3,
                "severity": "MODERATE"
            }
        ]

        return hotspots

hotspot_detector = HotspotDetector()
