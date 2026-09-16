import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from app.agents.query_router import query_router
from app.agents.specialists import specialist_manager

def test_query_routing_matrix():
    test_cases = [
        ("Did this area flood after heavy rain?", "flood", "Flood & Water Expansion Screening"),
        ("What is the land density in this area?", "urban", "Urban Expansion & Built-Up Density Analysis"),
        ("Show crop health degradation.", "agriculture", "Agricultural Health & Spectral Vegetation Monitoring"),
        ("Has the city expanded?", "urban", "Urban Expansion & Built-Up Density Analysis"),
        ("Has the coastline changed?", "coastal", "Coastal Erosion & Shoreline Position Monitoring"),
        ("Is this area likely to have flooding?", "flood_risk", "Flood Risk Screening & Predictive Disclaimer"),
        ("Analyze this place.", "ambiguous", "Ambiguous Query — Clarification Required"),
    ]

    print("--- TESTING QUERY INTENT ROUTING MATRIX ---")
    for query, expected_specialist, expected_label in test_cases:
        res = query_router.parse_query(query)
        spec = res["specialist_agent"]
        label = res["intent_label"]
        print(f"\nQuery: '{query}'")
        print(f"  -> Selected Specialist: {spec}")
        print(f"  -> Intent Label: {label}")
        assert spec == expected_specialist, f"Expected {expected_specialist}, got {spec}"
        assert label == expected_label, f"Expected {expected_label}, got {label}"

    print("\n[SUCCESS] All Query Intent Router Tests Passed Successfully!")

if __name__ == "__main__":
    test_query_routing_matrix()
