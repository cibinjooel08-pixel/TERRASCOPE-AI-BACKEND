from fastapi import APIRouter, HTTPException, Response
from typing import Dict, Any
from pydantic import BaseModel
from app.reports.pdf_generator import pdf_generator
from app.database.db import db_manager

router = APIRouter(prefix="/api/export", tags=["Export & Reports"])

class PDFExportRequest(BaseModel):
    analysis_id: str

@router.post("/pdf")
def export_pdf_report(req: PDFExportRequest):
    """
    Generates and downloads a complete PDF report for a given analysis ID.
    """
    record = db_manager.get_analysis_by_id(req.analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis ID not found.")

    res_data = record["result_json"]
    specialist_res = res_data.get("evidence", {}).get("specialist_result", {})
    provenance = res_data.get("evidence", {}).get("provenance", {})
    confidence = specialist_res.get("confidence", {})
    change_metrics = specialist_res.get("change_metrics", {})

    pdf_payload = {
        "query": record["query"],
        "specialist": record["specialist"],
        "conclusion": specialist_res.get("conclusion", "Surface change analysis complete."),
        "change_metrics": change_metrics,
        "confidence": confidence,
        "provenance": provenance
    }

    pdf_bytes = pdf_generator.generate_pdf_report(pdf_payload)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=SatQuery_Report_{req.analysis_id}.pdf"
        }
    )
