"""
Core Pipeline Orchestrator Service
Coordinates execution across the 7 screening stages:
1. Document Type Classification & OCR Processing
2. MRZ Validation
3. Document Forensics
4. Face Verification
5. Selfie Authenticity (Anti-Spoofing)
6. Data Consistency Cross-Check
7. Final Explainable Risk Assessment
"""

import uuid
from typing import Dict, Any, Optional
from ai_modules.ocr import extract_document_text, classify_document
from ai_modules.mrz_validation import validate_mrz
from ai_modules.document_forensics import analyze_document_forensics
from ai_modules.face_verification import verify_faces
from ai_modules.deepfake_detection import detect_deepfake_artifacts
from ai_modules.risk_scoring import calculate_explainable_risk_score, check_cross_document_consistency
from database import save_screening_case
from reports import generate_pdf_report
from backend.core.cleanup import cleanup_temp_files

def run_screening_pipeline(primary_doc_bytes: bytes, selfie_bytes: Optional[bytes] = None, supporting_doc_bytes: Optional[bytes] = None) -> Dict[str, Any]:
    screening_id = f"SIH2-{uuid.uuid4().hex[:8].upper()}"
    
    # Stage 1: OCR Processing & Document Classification
    ocr_res = extract_document_text(primary_doc_bytes)
    mrz_lines = ocr_res["extracted_text"].split('\n')
    
    # Stage 2: MRZ Validation
    mrz_res = validate_mrz(mrz_lines)

    # Document Classification
    doc_class_res = classify_document(ocr_res["extracted_text"], mrz_detected=mrz_res["mrz_detected"])
    ocr_res["classification"] = doc_class_res

    # OCR Supporting Doc if provided
    supporting_ocr = extract_document_text(supporting_doc_bytes) if supporting_doc_bytes else None

    # Stage 3: Document Forensics
    forensics_res = analyze_document_forensics(primary_doc_bytes)
    forensic_status = "PASS" if forensics_res["risk_level"] == "LOW" else "WARN" if forensics_res["risk_level"] == "MEDIUM" else "FAIL"

    # Stage 4: Face Verification
    face_res = verify_faces(primary_doc_bytes, selfie_bytes)
    face_status = "PASS" if face_res["status"] == "MATCH" else "WARN" if face_res["status"] in ("POSSIBLE MISMATCH", "INCONCLUSIVE") else "FAIL"

    # Stage 5: Selfie Authenticity / Anti-Spoofing
    if selfie_bytes:
        deepfake_res = detect_deepfake_artifacts(selfie_bytes)
        liveness_status = "WARN" if deepfake_res["is_suspicious"] else "PASS"
    else:
        deepfake_res = {
            "face_detected": False,
            "authenticity_score": 0.0,
            "is_suspicious": False,
            "screening_label": "Prototype AI-assisted screening",
            "detected_indicators": ["No selfie provided."],
            "quality_metrics": {},
            "disclaimer": "Prototype AI-assisted screening: Heuristic analysis for early artifact detection. Not a certified anti-spoofing biometrics engine."
        }
        liveness_status = "SKIPPED"

    # Stage 6: Cross-Document Data Consistency Check
    consistency_res = check_cross_document_consistency(
        primary_fields=ocr_res["fields"],
        supporting_fields=supporting_ocr["fields"] if supporting_ocr else None,
        mrz_fields=mrz_res.get("parsed_fields") if mrz_res.get("mrz_detected") else None
    )
    consistency_status = "PASS" if not consistency_res["mismatched_fields"] else "WARN"

    # Stage 7: Final Explainable Risk Assessment
    risk_res = calculate_explainable_risk_score(
        face_result=face_res,
        forensics_result=forensics_res,
        consistency_result=consistency_res,
        mrz_result=mrz_res,
        ocr_result=ocr_res,
        selfie_result=deepfake_res
    )

    decision = risk_res["recommended_decision"]
    overall_risk_score = risk_res["final_risk_score"]

    pipeline_steps = [
        {"step_name": "OCR Processing", "status": "PASS" if ocr_res["confidence"] >= 60 else "WARN", "score": ocr_res["confidence"], "details": {"extracted_count": len([k for k, v in ocr_res["fields"].items() if v]), "doc_type": doc_class_res["document_label"]}},
        {"step_name": "MRZ Validation", "status": "PASS" if mrz_res["mrz_detected"] and not mrz_res["validation_errors"] else "WARN" if mrz_res["mrz_detected"] else "SKIPPED", "score": 90.0 if mrz_res["mrz_detected"] else 0.0, "details": {"mrz_format": mrz_res.get("format", "None")}},
        {"step_name": "Document Forensics", "status": forensic_status, "score": 100.0 - forensics_res["tampering_risk_score"], "details": {"risk_level": forensics_res["risk_level"]}},
        {"step_name": "Face Verification", "status": face_status, "score": face_res["similarity_score"], "details": {"verdict": face_res["status"]}},
        {"step_name": "Selfie Authenticity", "status": liveness_status, "score": deepfake_res["authenticity_score"], "details": {"label": deepfake_res["screening_label"]}},
        {"step_name": "Data Consistency", "status": consistency_status, "score": consistency_res["consistency_score"], "details": {"mismatch_count": len(consistency_res["mismatched_fields"])}},
        {"step_name": "Final Risk Assessment", "status": decision, "score": 100.0 - overall_risk_score, "details": {"risk_classification": risk_res["risk_classification"], "recommendation": decision}}
    ]

    result_payload = {
        "screening_id": screening_id,
        "overall_risk_score": overall_risk_score,
        "decision": decision,
        "ocr_result": ocr_res,
        "mrz_result": mrz_res,
        "forensics_result": forensics_res,
        "face_verification_result": face_res,
        "selfie_authenticity_result": deepfake_res,
        "consistency_result": consistency_res,
        "risk_scoring_result": risk_res,
        "pipeline_steps": pipeline_steps,
        "summary_notes": [
            f"Screening ID {screening_id} completed.",
            f"Document Type Identified: {doc_class_res['document_label']}",
            f"Classification: {risk_res['risk_classification']} (Risk Score: {overall_risk_score:.1f}/100)",
            f"Decision Recommendation: {decision}"
        ]
    }

    # Save case history to SQLite Database
    save_screening_case(
        case_id=screening_id,
        risk_score=overall_risk_score,
        classification=risk_res["risk_classification"],
        decision=decision,
        summary_data=result_payload
    )

    # Generate PDF Report File
    try:
        pdf_path = generate_pdf_report(result_payload)
        result_payload["pdf_report_path"] = pdf_path
    except Exception as e:
        print(f"PDF Report generation warning: {str(e)}")

    # Clean temporary files
    try:
        cleanup_temp_files(max_age_seconds=3600)
    except Exception:
        pass

    return result_payload
