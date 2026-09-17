import numpy as np
from typing import Dict, Any, Tuple

FORMULAS = {
    "NDVI": {
        "name": "Normalized Difference Vegetation Index",
        "formula": "(B08 - B04) / (B08 + B04)",
        "bands": "B08 (NIR), B04 (Red)",
        "description": "Measures photosynthetic vegetation density and crop health."
    },
    "NDWI": {
        "name": "Normalized Difference Water Index",
        "formula": "(B03 - B08) / (B03 + B08)",
        "bands": "B03 (Green), B08 (NIR)",
        "description": "Delineates open water bodies, flood inundation, and plant moisture content."
    },
    "NDBI": {
        "name": "Normalized Difference Built-up Index",
        "formula": "(B11 - B08) / (B11 + B08)",
        "bands": "B11 (SWIR), B08 (NIR)",
        "description": "Highlights impervious surface structures, urban areas, and bare soil."
    },
    "TRUE_COLOR": {
        "name": "True Color RGB",
        "formula": "B04 (Red), B03 (Green), B02 (Blue)",
        "bands": "Visible Light",
        "description": "Natural color composition matching human eye perception."
    },
    "FALSE_COLOR": {
        "name": "False Color Infrared",
        "formula": "B08 (NIR), B04 (Red), B03 (Green)",
        "bands": "Infrared & Visible Light",
        "description": "Emphasizes vegetation in deep red tones and water in dark tones."
    }
}

class OpticalProcessor:
    """
    Remote sensing calculations for Sentinel-2 optical imagery.
    """

    def compute_ndvi(self, b08: np.ndarray, b04: np.ndarray) -> np.ndarray:
        """Calculates NDVI normalized index array."""
        denom = (b08 + b04) + 1e-6
        return (b08 - b04) / denom

    def compute_ndwi(self, b03: np.ndarray, b08: np.ndarray) -> np.ndarray:
        """Calculates NDWI normalized water index array."""
        denom = (b03 + b08) + 1e-6
        return (b03 - b08) / denom

    def compute_ndbi(self, b11: np.ndarray, b08: np.ndarray) -> np.ndarray:
        """Calculates NDBI normalized built-up index array."""
        denom = (b11 + b08) + 1e-6
        return (b11 - b08) / denom

    def get_formula_info(self, index_name: str) -> Dict[str, Any]:
        """Returns mathematical formula metadata for display in the UI."""
        idx_upper = index_name.upper()
        return FORMULAS.get(idx_upper, {
            "name": index_name,
            "formula": "Custom Spectral Index",
            "bands": "Multi-spectral",
            "description": "Remote sensing spectral index computation."
        })

optical_processor = OpticalProcessor()
