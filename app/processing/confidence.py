from typing import Dict, Any, List

class ConfidenceCalculator:
    """
    Computes quantifiable confidence scores, uncertainty metrics, and reliability badges
    from measurable satellite data quality factors.
    """

    def calculate_confidence(
        self,
        cloud_cover: float,
        temporal_gap_days: float,
        is_real_data: bool = True,
        cross_sensor_agreement: str = "HIGH",
        valid_pixels_pct: float = 98.0
    ) -> Dict[str, Any]:
        """
        Calculates mathematical confidence score (0-100%) and uncertainty breakdown.
        """
        reasons = []
        score = 0.0

        # Factor 1: Data Provenance & Real Satellite Feed (Weight 30%)
        if is_real_data:
            score += 30.0
            reasons.append("✓ Active Sentinel satellite observation from Copernicus CDSE.")
        else:
            score += 15.0
            reasons.append("⚠️ Using synthetic baseline preview (CDSE credentials unconfigured).")

        # Factor 2: Optical Cloud Coverage (Weight 25%)
        cloud_penalty = min(25.0, (cloud_cover / 100.0) * 25.0)
        cloud_score = 25.0 - cloud_penalty
        score += cloud_score
        if cloud_cover < 5.0:
            reasons.append(f"✓ Excellent atmospheric conditions ({cloud_cover}% cloud cover).")
        elif cloud_cover < 20.0:
            reasons.append(f"✓ Low cloud obscuration ({cloud_cover}% cloud cover).")
        else:
            reasons.append(f"⚠️ Moderate cloud cover detected ({cloud_cover}%).")

        # Factor 3: Temporal Gap (Weight 25%)
        gap_penalty = min(25.0, (temporal_gap_days / 15.0) * 25.0)
        gap_score = 25.0 - gap_penalty
        score += gap_score
        if temporal_gap_days < 1.0:
            reasons.append(f"✓ Exact acquisition date match ({temporal_gap_days} days gap).")
        elif temporal_gap_days <= 5.0:
            reasons.append(f"✓ Narrow temporal gap ({temporal_gap_days} days from requested date).")
        else:
            reasons.append(f"⚠️ Wider temporal window required ({temporal_gap_days} days difference).")

        # Factor 4: Pixel Completeness & Sensor Agreement (Weight 20%)
        if cross_sensor_agreement == "HIGH":
            score += 20.0
            reasons.append("✓ High cross-sensor agreement between Sentinel-1 SAR and Sentinel-2 Optical.")
        elif cross_sensor_agreement == "MEDIUM":
            score += 14.0
            reasons.append("✓ Moderate multi-sensor signal alignment.")
        else:
            score += 8.0
            reasons.append("⚠️ Sensor disagreement or single-sensor observation mode.")

        final_score = round(max(10.0, min(99.0, score)), 1)

        # Classify overall confidence
        if final_score >= 82.0:
            rating = "HIGH"
            uncertainty = "Low"
            badge = "Excellent"
        elif final_score >= 65.0:
            rating = "MEDIUM"
            uncertainty = "Moderate"
            badge = "Good"
        else:
            rating = "LOW"
            uncertainty = "Elevated"
            badge = "Moderate"

        return {
            "overall_confidence_pct": final_score,
            "rating": rating,
            "uncertainty": uncertainty,
            "data_reliability_badge": badge,
            "breakdown": {
                "provenance_score": round(30.0 if is_real_data else 15.0, 1),
                "atmospheric_score": round(cloud_score, 1),
                "temporal_score": round(gap_score, 1),
                "sensor_agreement_score": round(20.0 if cross_sensor_agreement == "HIGH" else 14.0, 1)
            },
            "reasons": reasons
        }

confidence_calculator = ConfidenceCalculator()
