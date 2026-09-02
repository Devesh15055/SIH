"""
Explainable Risk Scoring Engine
Combines multi-signal outputs from:
- Face Verification (25%)
- Document Forensics (25%)
- Data Consistency (20%)
- MRZ Validation (15%)
- OCR Confidence (10%)
- Selfie Authenticity (5%)

Generates FINAL RISK SCORE (0 to 100), Risk Classification (LOW, MEDIUM, HIGH, CRITICAL),
and human-readable explanation of risk contributors.
"""

from typing import Dict, List, Any, Optional

DEFAULT_WEIGHTS = {
    "face_verification": 0.25,
    "document_forensics": 0.25,
    "data_consistency": 0.20,
    "mrz_validation": 0.15,
    "ocr_confidence": 0.10,
    "selfie_authenticity": 0.05
}

def calculate_explainable_risk_score(
    face_result: Dict[str, Any],
    forensics_result: Dict[str, Any],
    consistency_result: Dict[str, Any],
    mrz_result: Dict[str, Any],
    ocr_result: Dict[str, Any],
    selfie_result: Dict[str, Any],
    custom_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Calculate final explainable risk score and produce human-readable explanation of risk drivers.
    """
    weights = custom_weights or DEFAULT_WEIGHTS

    # Normalize weight sum to 1.0 if custom weights supplied
    total_w = sum(weights.values())
    if total_w > 0:
        weights = {k: v / total_w for k, v in weights.items()}

    human_explanation = []
    risk_breakdown = {}

    # 1. Face Verification Risk Component (0 to 100)
    face_status = face_result.get("status", "INCONCLUSIVE")
    if face_status == "MISMATCH":
        face_risk = 90.0
        human_explanation.append("Face verification failed: ID photo does not match user selfie (Verdict: MISMATCH).")
    elif face_status == "POSSIBLE MISMATCH":
        face_risk = 50.0
        human_explanation.append(f"Face verification uncertain: Similarity score ({face_result.get('similarity_score', 0):.1f}%) is in borderline threshold.")
    elif face_status == "INCONCLUSIVE":
        face_risk = 35.0
        human_explanation.append("Face verification inconclusive (selfie or face detection unavailable).")
    else:  # "MATCH"
        face_risk = 0.0

    # 2. Document Forensics Risk Component (0 to 100)
    forensic_risk = float(forensics_result.get("tampering_risk_score", 10.0))
    if forensic_risk >= 65.0:
        human_explanation.append(f"High document tampering risk detected ({forensic_risk:.1f}/100) via ELA / metadata anomalies.")
    elif forensic_risk >= 35.0:
        human_explanation.append(f"Moderate document forensic anomalies detected ({forensic_risk:.1f}/100).")

    # 3. Data Consistency Risk Component (0 to 100)
    consistency_score = float(consistency_result.get("consistency_score", 100.0))
    consistency_risk = max(0.0, 100.0 - consistency_score)
    mismatches = consistency_result.get("mismatched_fields", [])
    if mismatches:
        m_list = ", ".join([m["field"] for m in mismatches])
        human_explanation.append(f"Data consistency mismatch detected across fields: {m_list}.")

    # 4. MRZ Validation Risk Component (0 to 100)
    if mrz_result.get("mrz_detected"):
        if mrz_result.get("validation_errors"):
            mrz_risk = 80.0
            human_explanation.append("ICAO 9303 MRZ checksum validation failed (checksum digit mismatch).")
        else:
            mrz_risk = 0.0
    else:
        mrz_risk = 15.0  # Minor baseline for non-MRZ docs

    # 5. OCR Confidence Risk Component (0 to 100)
    ocr_conf = float(ocr_result.get("confidence", 80.0))
    ocr_risk = max(0.0, 100.0 - ocr_conf)
    if ocr_conf < 60.0:
        human_explanation.append(f"Low OCR text extraction confidence ({ocr_conf:.1f}%). Missing key text fields.")

    # 6. Selfie Authenticity Risk Component (0 to 100)
    auth_score = float(selfie_result.get("authenticity_score", 85.0))
    selfie_risk = max(0.0, 100.0 - auth_score)
    if selfie_result.get("is_suspicious"):
        human_explanation.append("Selfie authenticity screening flagged suspicious image smoothing / digital artifacts.")

    # Compute weighted aggregate final risk score
    component_risks = {
        "face_verification": face_risk,
        "document_forensics": forensic_risk,
        "data_consistency": consistency_risk,
        "mrz_validation": mrz_risk,
        "ocr_confidence": ocr_risk,
        "selfie_authenticity": selfie_risk
    }

    final_risk_score = sum(component_risks[k] * weights[k] for k in weights)
    final_risk_score = round(min(100.0, max(0.0, final_risk_score)), 1)

    # Classify Risk Category
    if final_risk_score >= 76.0:
        classification = "CRITICAL RISK"
        decision = "REJECTED"
    elif final_risk_score >= 51.0:
        classification = "HIGH RISK"
        decision = "REJECTED"
    elif final_risk_score >= 26.0:
        classification = "MEDIUM RISK"
        decision = "MANUAL REVIEW"
    else:
        classification = "LOW RISK"
        decision = "APPROVED"

    if not human_explanation:
        human_explanation.append("All multi-signal AI checks passed within normal parameters.")

    # Build detailed risk breakdown
    for k, w in weights.items():
        score = component_risks[k]
        contrib = round(score * w, 2)
        risk_breakdown[k] = {
            "component_risk_score": round(score, 1),
            "configured_weight": w,
            "weighted_contribution": contrib
        }

    return {
        "final_risk_score": final_risk_score,
        "risk_classification": classification,
        "recommended_decision": decision,
        "human_explanation": human_explanation,
        "risk_breakdown": risk_breakdown,
        "configured_weights": weights
    }
