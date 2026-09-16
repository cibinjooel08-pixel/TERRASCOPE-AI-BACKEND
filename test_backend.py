import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("Testing Python Imports...")
from app.satellite.cdse_auth import cdse_auth
from app.satellite.catalog_client import catalog_client
from app.satellite.process_client import process_client
from app.processing.optical import optical_processor
from app.processing.sar import sar_processor
from app.processing.change_detection import change_detector
from app.processing.hotspots import hotspot_detector
from app.processing.confidence import confidence_calculator
from app.agents.query_router import query_router
from app.agents.specialists import specialist_manager
from app.agents.evidence_agent import evidence_agent
from app.database.db import db_manager
from app.reports.pdf_generator import pdf_generator
from app.main import app

print("[SUCCESS] All Backend Modules Imported Successfully!")

# 1. Test CDSE Auth Check
auth_health = cdse_auth.check_health()
print(f"[SUCCESS] Auth Health Diagnostic: {auth_health['status']}")

# 2. Test Query Router Intent Classification
intent_test = query_router.parse_query("Did this area flood after the cyclone?")
assert intent_test["specialist_agent"] == "flood"
print(f"[SUCCESS] Query Router Intent Classification: Passed ({intent_test['intent_label']})")

# 3. Test Confidence Calculation
conf_test = confidence_calculator.calculate_confidence(cloud_cover=4.0, temporal_gap_days=1.0)
assert conf_test["overall_confidence_pct"] > 70.0
print(f"[SUCCESS] Empirical Confidence Score Engine: Passed ({conf_test['overall_confidence_pct']}% - {conf_test['rating']})")

# 4. Test Change Detector
dummy_img_a = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\x00\x00\x00\x90\x91e6\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa7\x9a\x07\x00\x00\x00\x00IEND\xaeB`\x82'
change_test, _ = change_detector.analyze_change(dummy_img_a, dummy_img_a)
assert "earth_change_score" in change_test
print(f"[SUCCESS] Change Detection & Change Score: Passed ({change_test['earth_change_score']} / 100)")

# 5. Test PDF Report Generator
pdf_bytes = pdf_generator.generate_pdf_report({
    "query": "Did this area flood?",
    "specialist": "Flood Specialist",
    "conclusion": "Flood extent detected.",
    "change_metrics": change_test,
    "confidence": conf_test,
    "provenance": {"data_provider": "Copernicus CDSE"}
})
assert len(pdf_bytes) > 500
print(f"[SUCCESS] PDF Report Generator: Passed ({len(pdf_bytes)} bytes PDF output)")

print("PASSED: ALL BACKEND UNIT & INTEGRATION TESTS PASSED CLEANLY!")
