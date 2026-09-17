from typing import Dict, Any, List

MODEL_REGISTRY = [
    {
        "model_name": "SatQuery Change Detection Baseline v1.2",
        "version": "1.2.0",
        "task": "Bi-Temporal Euclidean Spectral Change & Masking",
        "input_type": "Sentinel-2 L2A / Sentinel-1 GRD Image Pair",
        "output_type": "Binary Change Mask & Change Percentage",
        "confidence": "High (Deterministic Baseline)",
        "processing_time": "0.42 seconds",
        "status": "ACTIVE_BASELINE"
    },
    {
        "model_name": "Sentinel-1 SAR Flood Screening Engine",
        "version": "2.1.0",
        "task": "SAR Backscatter Drop & Flood Inundation Delineation",
        "input_type": "Sentinel-1 VV/VH Polarimetric Backscatter",
        "output_type": "Flood Extent Polygon & Affected Area %",
        "confidence": "High (Radar Physical Model)",
        "processing_time": "0.38 seconds",
        "status": "ACTIVE_BASELINE"
    },
    {
        "model_name": "Agriculture Crop Health NDVI Anomaly Network",
        "version": "1.0.0",
        "task": "Field-Level Spectral Index Anomaly Detection",
        "input_type": "Sentinel-2 Multi-Spectral (B04, B08)",
        "output_type": "Field Statistics (Mean/Min/Max NDVI) & Degradation Alert",
        "confidence": "High (Spectral Index standard)",
        "processing_time": "0.29 seconds",
        "status": "ACTIVE_BASELINE"
    },
    {
        "model_name": "InSAR Ground Deformation Coherence Pipeline Framework",
        "version": "3.0.0-modular",
        "task": "Interferometric SAR Phase Coherence & Terrain Susceptibility",
        "input_type": "Sentinel-1 SLC Phase Pair + Copernicus DEM",
        "output_type": "Observed Backscatter Anomaly & Slope Risk Context",
        "confidence": "Moderate (Baseline SAR Screening)",
        "processing_time": "0.65 seconds",
        "status": "MODULAR_INTERFACE"
    }
]

def get_model_registry() -> List[Dict[str, Any]]:
    return MODEL_REGISTRY
