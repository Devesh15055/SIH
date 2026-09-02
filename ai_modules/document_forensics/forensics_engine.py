"""
Document Forensics Aggregator Engine
Integrates Error Level Analysis (ELA), EXIF Metadata inspection, and Compression Analysis.
Outputs structured tampering risk score and risk level (LOW, MEDIUM, HIGH).
"""

from typing import Dict, Any, List
from .ela import perform_ela
from .metadata_analyzer import analyze_metadata
from .compression_analyzer import analyze_compression

def analyze_document_forensics(image_input: Any) -> Dict[str, Any]:
    """
    Main entrypoint for Document Forensics analysis.
    Returns structured output with tampering_risk_score, risk_level, indicators, and warnings.
    """
    indicators = []
    analysis_warnings = []
    
    # Mandatory Disclaimer
    disclaimer = "Forensic indicators require additional verification by human expert auditor. ELA anomalies suggest compression variations, not conclusive proof of forgery."
    analysis_warnings.append(disclaimer)

    # 1. Run ELA
    ela_res = perform_ela(image_input)
    analysis_warnings.extend(ela_res.get("warnings", []))

    # 2. Run Metadata Analysis
    meta_res = analyze_metadata(image_input)
    indicators.extend(meta_res.get("indicators", []))
    analysis_warnings.extend(meta_res.get("warnings", []))

    # 3. Run Compression Analysis
    comp_res = analyze_compression(image_input)
    indicators.extend(comp_res.get("indicators", []))
    analysis_warnings.extend(comp_res.get("warnings", []))

    # Calculate Tampering Risk Score (0.0 to 100.0)
    risk_score = 10.0  # Baseline low risk

    # ELA contribution
    if ela_res["suspicious_patch_count"] > 10:
        risk_score += 35.0
        indicators.append(f"Error Level Analysis detected {ela_res['suspicious_patch_count']} high-contrast anomaly patches.")
    elif ela_res["suspicious_patch_count"] > 3:
        risk_score += 15.0
        indicators.append(f"Error Level Analysis detected {ela_res['suspicious_patch_count']} localized patch variations.")

    # Metadata contribution
    if meta_res.get("software_detected"):
        risk_score += 30.0

    # Compression contribution
    if comp_res["block_grid_discontinuity"] > 25.0:
        risk_score += 15.0

    risk_score = min(100.0, max(0.0, risk_score))

    # Determine Risk Level Category
    if risk_score >= 65.0:
        risk_level = "HIGH"
    elif risk_score >= 35.0:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "tampering_risk_score": round(risk_score, 1),
        "risk_level": risk_level,
        "indicators": indicators,
        "analysis_warnings": analysis_warnings,
        "ela_image_path": ela_res.get("ela_image_path"),
        "details": {
            "ela_mean_error": ela_res.get("ela_mean_error"),
            "ela_suspicious_patches": ela_res.get("suspicious_patch_count"),
            "software_detected": meta_res.get("software_detected"),
            "has_exif": meta_res.get("has_exif"),
            "block_grid_discontinuity": comp_res.get("block_grid_discontinuity")
        }
    }
