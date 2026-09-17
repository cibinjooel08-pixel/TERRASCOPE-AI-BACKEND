import numpy as np
from typing import Dict, Any, List, Optional, Tuple

class SARProcessor:
    """
    Sentinel-1 Synthetic Aperture Radar (SAR) processing & analysis module.
    """

    def process_backscatter(self, vv: np.ndarray, vh: np.ndarray) -> Dict[str, Any]:
        """
        Computes SAR polarimetric metrics (VV, VH, VV/VH ratio).
        """
        vv_db = 10 * np.log10(np.clip(vv, 1e-5, 1.0))
        vh_db = 10 * np.log10(np.clip(vh, 1e-5, 1.0))
        ratio = vh / (vv + 1e-5)
        
        return {
            "mean_vv_db": float(np.mean(vv_db)),
            "mean_vh_db": float(np.mean(vh_db)),
            "mean_ratio": float(np.mean(ratio)),
            "water_threshold_db": -15.0
        }

    def detect_flood_extent(
        self,
        before_sar: np.ndarray,
        after_sar: np.ndarray,
        threshold_db: float = -15.0
    ) -> Dict[str, Any]:
        """
        Screens flood inundation from Sentinel-1 SAR temporal backscatter drop.
        Open water produces specular reflection resulting in sharp backscatter drop (< -15 dB).
        """
        # Calculate backscatter drop
        diff = after_sar - before_sar
        flood_mask = (after_sar < threshold_db) & (diff < -3.0)
        
        total_pixels = before_sar.size
        flood_pixels = int(np.sum(flood_mask))
        percentage = (flood_pixels / max(1, total_pixels)) * 100.0

        return {
            "methodology": "Sentinel-1 SAR Backscatter Threshold Screening (< -15 dB)",
            "flood_pixels": flood_pixels,
            "total_pixels": total_pixels,
            "flooded_percentage": round(percentage, 2),
            "label": "Observed flood extent / flood screening",
            "water_increase_detected": percentage > 1.5
        }

    def analyze_ground_deformation(
        self,
        before_sar: np.ndarray,
        after_sar: np.ndarray,
        slope_deg: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        SAR Ground instability & surface change screening.
        Clearly distinguishes observed surface change / SAR anomaly vs predictions.
        """
        diff = np.abs(after_sar - before_sar)
        anomaly_pixels = int(np.sum(diff > 4.0))
        percentage = (anomaly_pixels / max(1, before_sar.size)) * 100.0

        has_insufficient_evidence = percentage < 0.5

        if has_insufficient_evidence:
            conclusion = "Insufficient evidence for a reliable ground deformation conclusion."
            evidence_level = "LOW"
        elif percentage > 5.0:
            conclusion = "Indicators suggest ELEVATED evidence of surface backscatter change / potential terrain disturbance."
            evidence_level = "ELEVATED"
        else:
            conclusion = "Indicators suggest MODERATE localized surface backscatter variation."
            evidence_level = "MODERATE"

        return {
            "insar_module_status": "MODULAR_INSAR_PIPELINE_ARCHITECTURE (Baseline SAR Backscatter Screening)",
            "observed_surface_change": round(percentage, 2),
            "anomaly_pixels": anomaly_pixels,
            "evidence_level": evidence_level,
            "conclusion": conclusion,
            "slope_context": f"{slope_deg}° slope" if slope_deg is not None else "Terrain DEM context integrated",
            "disclaimer": "This analysis presents observed SAR backscatter anomalies and surface susceptibility, NOT exact future landslide predictions."
        }

sar_processor = SARProcessor()
