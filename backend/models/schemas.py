"""
Shared Pydantic Schemas for API Requests, Responses, and AI Module Pipeline payloads.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class HealthResponse(BaseModel):
    status: str = "online"
    service: str = "SIH26188 AI Identity Screening Backend"
    version: str = "1.0.0"
    environment: str = "development"

class OCRFields(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    document_number: Optional[str] = None
    expiry_date: Optional[str] = None
    address: Optional[str] = None

class OCRResponse(BaseModel):
    extracted_text: str
    fields: OCRFields
    confidence: float
    warnings: List[str] = []

class MRZChecksumStatus(BaseModel):
    document_number: bool
    dob: bool
    expiry_date: bool
    composite: bool

class MRZResponse(BaseModel):
    mrz_detected: bool
    format: Optional[str] = None
    parsed_fields: Dict[str, Any] = {}
    checksum_status: MRZChecksumStatus
    validation_errors: List[str] = []
    status_message: str

class ForensicsResponse(BaseModel):
    tampering_risk_score: float
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    indicators: List[str] = []
    analysis_warnings: List[str] = []
    ela_image_path: Optional[str] = None
    details: Dict[str, Any] = {}

class FaceVerificationResponse(BaseModel):
    document_face_detected: bool
    selfie_face_detected: bool
    similarity_score: float
    status: str  # "MATCH", "POSSIBLE MISMATCH", "MISMATCH", "INCONCLUSIVE"
    quality_warnings: List[str] = []

class SelfieAuthenticityResponse(BaseModel):
    face_detected: bool
    authenticity_score: float
    is_suspicious: bool
    screening_label: str = "Prototype AI-assisted screening"
    detected_indicators: List[str] = []
    quality_metrics: Dict[str, Any] = {}
    disclaimer: str

class ConsistencyResponse(BaseModel):
    consistency_score: float
    matching_fields: List[Dict[str, Any]] = []
    mismatched_fields: List[Dict[str, Any]] = []
    missing_fields: List[Dict[str, Any]] = []
    summary_message: str

class RiskScoringResponse(BaseModel):
    final_risk_score: float
    risk_classification: str  # "LOW RISK", "MEDIUM RISK", "HIGH RISK", "CRITICAL RISK"
    recommended_decision: str  # "APPROVED", "MANUAL REVIEW", "REJECTED"
    human_explanation: List[str] = []
    risk_breakdown: Dict[str, Any] = {}
    configured_weights: Dict[str, float] = {}

class PipelineStepResult(BaseModel):
    step_name: str
    status: str  # "PASS", "WARN", "FAIL", "SKIPPED"
    score: float
    details: Dict[str, Any]

class ScreeningResponse(BaseModel):
    screening_id: str
    overall_risk_score: float
    decision: str  # "APPROVED", "MANUAL REVIEW", "REJECTED"
    ocr_result: OCRResponse
    mrz_result: MRZResponse
    forensics_result: ForensicsResponse
    face_verification_result: FaceVerificationResponse
    selfie_authenticity_result: SelfieAuthenticityResponse
    consistency_result: ConsistencyResponse
    risk_scoring_result: RiskScoringResponse
    pipeline_steps: List[PipelineStepResult]
    summary_notes: List[str] = []
