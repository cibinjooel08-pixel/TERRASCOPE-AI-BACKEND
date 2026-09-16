import re
from typing import Dict, Any, List

class QueryRouterAgent:
    """
    Query Understanding Agent that parses natural language queries and selects
    the optimal satellite sensors, specialist agent, and processing pipeline.
    """

    def parse_query(self, query_text: str) -> Dict[str, Any]:
        raw_q = query_text.lower().strip()
        q = re.sub(r'[^\w\s]', '', raw_q).strip()

        # Ambiguous or ultra-short query check
        if len(q) < 6 or q in ["analyze", "check", "test", "analyze this place", "check this", "analyze this"]:
            return {
                "original_query": query_text,
                "specialist_agent": "ambiguous",
                "intent_label": "Ambiguous Query — Clarification Required",
                "primary_sensor": "sentinel-2",
                "secondary_sensor": "sentinel-1",
                "routing_rationale": "Query is ambiguous. The platform requires a specific domain prompt (Flood, Agriculture, Urban Density, Coastal, Landslide).",
                "confidence_threshold": 0.50
            }

        # Flood Risk / Prediction Intent (Distinguish historical detection from future prediction)
        if any(w in q for w in ["likely to flood", "likely to have flooding", "will flood", "predict flood", "flood risk", "flood forecast", "future flood", "risk of flood"]):
            specialist = "flood_risk"
            primary_sensor = "sentinel-1"
            secondary_sensor = "sentinel-2"
            intent_label = "Flood Risk Screening & Predictive Disclaimer"
            rationale = "Predictive queries trigger historical flood inundation screening combined with predictive modeling disclaimers."

        # Flood / Inundation Historical Detection Intent
        elif any(w in q for w in ["flood", "water", "inundat", "submerge", "cyclone", "river", "overflow", "drown", "storm surge"]):
            specialist = "flood"
            primary_sensor = "sentinel-1"
            secondary_sensor = "sentinel-2"
            intent_label = "Flood & Water Expansion Screening"
            rationale = "Flood queries prioritize Sentinel-1 SAR due to cloud-penetrating synthetic aperture radar imaging of specular water reflections."

        # Urban Expansion / Built-up / Land Density Intent
        elif any(w in q for w in ["urban", "city", "building", "built-up", "built up", "density", "expand", "settlement", "construction", "impervious", "land density"]):
            specialist = "urban"
            primary_sensor = "sentinel-2"
            secondary_sensor = "sentinel-1"
            intent_label = "Urban Expansion & Built-Up Density Analysis"
            rationale = "Urban queries deploy Sentinel-2 NDBI (B11 SWIR & B08 NIR) to evaluate building concentration and impervious surface expansion."

        # Coastal / Shoreline Change Intent
        elif any(w in q for w in ["coastal", "coast", "shore", "shoreline", "erosion", "beach", "sea level", "accretion"]):
            specialist = "coastal"
            primary_sensor = "sentinel-2"
            secondary_sensor = "sentinel-1"
            intent_label = "Coastal Erosion & Shoreline Position Monitoring"
            rationale = "Coastal queries combine Sentinel-2 NDWI water-land boundary extraction with multi-date shoreline displacement tracking."

        # Landslide / Ground Deformation Intent
        elif any(w in q for w in ["landslide", "slope", "hillside", "deform", "instability", "ground move", "collapse", "mudslide"]):
            specialist = "landslide"
            primary_sensor = "sentinel-1"
            secondary_sensor = "sentinel-2"
            intent_label = "Terrain Instability & SAR Backscatter Screening"
            rationale = "Ground movement queries deploy Sentinel-1 SAR multi-date backscatter anomaly detection integrated with DEM slope susceptibility."

        # Agriculture / Crop Health / Vegetation Intent
        elif any(w in q for w in ["crop", "agricultur", "farm", "ndvi", "health", "vegetation", "canopy", "yield", "field", "harvest", "deforest"]):
            specialist = "agriculture"
            primary_sensor = "sentinel-2"
            secondary_sensor = None
            intent_label = "Agricultural Health & Spectral Vegetation Monitoring"
            rationale = "Agriculture queries deploy Sentinel-2 Multi-Spectral Optical imagery (Red-Edge B08 & Red B04) to calculate plant chlorophyll absorption."

        # Default: General Bi-Temporal Change Detection
        else:
            specialist = "change_detection"
            primary_sensor = "sentinel-2"
            secondary_sensor = "sentinel-1"
            intent_label = "General Visual Change Detection"
            rationale = "Natural language query requests general spectral & spatial change comparison."

        return {
            "original_query": query_text,
            "specialist_agent": specialist,
            "intent_label": intent_label,
            "primary_sensor": primary_sensor,
            "secondary_sensor": secondary_sensor,
            "routing_rationale": rationale,
            "confidence_threshold": 0.65
        }

query_router = QueryRouterAgent()
