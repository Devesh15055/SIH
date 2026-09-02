"""
API Router V1 Endpoints
Provides /health, /screen, /cases, /cases/{case_id}/report REST API routes.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional, List, Dict, Any
import os
from backend.models.schemas import HealthResponse, ScreeningResponse
from backend.services.pipeline_service import run_screening_pipeline
from database import get_all_screening_cases, get_case_by_id
from reports import generate_pdf_report

router = APIRouter(prefix="/api/v1", tags=["Screening Engine"])

@router.get("/health", response_model=HealthResponse)
def get_api_health():
    return HealthResponse()

@router.post("/screen", response_model=ScreeningResponse)
async def screen_identity_documents(
    primary_document: UploadFile = File(..., description="Primary Identity Document Image"),
    selfie: Optional[UploadFile] = File(None, description="Live Selfie Photo"),
    supporting_document: Optional[UploadFile] = File(None, description="Optional Supporting Document")
):
    try:
        primary_bytes = await primary_document.read()
        selfie_bytes = await selfie.read() if selfie else None
        supporting_bytes = await supporting_document.read() if supporting_document else None

        if not primary_bytes:
            raise HTTPException(status_code=400, detail="Primary document file is empty.")

        result = run_screening_pipeline(primary_bytes, selfie_bytes, supporting_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screening pipeline execution error: {str(e)}")

@router.get("/cases", response_model=List[Dict[str, Any]])
def list_history_cases():
    return get_all_screening_cases()

@router.get("/cases/{case_id}/report")
def download_case_pdf_report(case_id: str):
    reports_dir = "C:/Users/Hp/Desktop/SIH2/generated_reports"
    pdf_path = os.path.join(reports_dir, f"SIH2_Report_{case_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"PDF report for case {case_id} not found.")
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"SIH2_Report_{case_id}.pdf")
