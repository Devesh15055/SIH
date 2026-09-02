"""
Cross-Document Data Consistency Module
Compares identity fields across Primary Document (OCR), Supporting Document (OCR), and MRZ lines.
Detects matching, mismatched, and missing fields to compute data consistency score (0 to 100).
"""

import re
from typing import Dict, List, Any, Optional

TARGET_FIELDS = ["full_name", "date_of_birth", "gender", "nationality", "document_number"]

def normalize_field_val(val: Optional[str]) -> str:
    """Normalize string for fuzzy/exact field comparison."""
    if not val:
        return ""
    # Strip spaces, punctuation, convert to uppercase
    cleaned = re.sub(r'[^A-Z0-9]', '', str(val).upper())
    return cleaned

def check_field_match(val1: str, val2: str) -> bool:
    """Compare normalized field values."""
    n1 = normalize_field_val(val1)
    n2 = normalize_field_val(val2)
    if not n1 or not n2:
        return False
    return n1 == n2 or n1 in n2 or n2 in n1

def check_cross_document_consistency(
    primary_fields: Dict[str, Any],
    supporting_fields: Optional[Dict[str, Any]] = None,
    mrz_fields: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Perform cross-document data consistency check between Primary Doc, Supporting Doc, and MRZ data.
    """
    matching_fields = []
    mismatched_fields = []
    missing_fields = []

    supp = supporting_fields or {}
    mrz = mrz_fields or {}

    sources = [("Primary Doc", primary_fields)]
    if supp:
        sources.append(("Supporting Doc", supp))
    if mrz:
        sources.append(("MRZ Data", mrz))

    total_checks = 0
    mismatch_count = 0

    for field in TARGET_FIELDS:
        p_val = primary_fields.get(field)
        s_val = supp.get(field) if supp else None
        m_val = mrz.get(field) if mrz else None

        field_name_clean = field.replace("_", " ").title()

        # Check Primary vs MRZ
        if p_val and m_val:
            total_checks += 1
            if check_field_match(p_val, m_val):
                matching_fields.append({
                    "field": field_name_clean,
                    "sources": ["Primary Doc", "MRZ Data"],
                    "value": str(p_val)
                })
            else:
                mismatch_count += 1
                mismatched_fields.append({
                    "field": field_name_clean,
                    "source1": f"Primary Doc ('{p_val}')",
                    "source2": f"MRZ Data ('{m_val}')",
                    "reason": f"{field_name_clean} mismatch between document OCR text and MRZ line."
                })

        # Check Primary vs Supporting
        if p_val and s_val:
            total_checks += 1
            if check_field_match(p_val, s_val):
                matching_fields.append({
                    "field": field_name_clean,
                    "sources": ["Primary Doc", "Supporting Doc"],
                    "value": str(p_val)
                })
            else:
                mismatch_count += 1
                mismatched_fields.append({
                    "field": field_name_clean,
                    "source1": f"Primary Doc ('{p_val}')",
                    "source2": f"Supporting Doc ('{s_val}')",
                    "reason": f"{field_name_clean} mismatch between primary document and supporting document."
                })

        # Track missing fields
        missing_in = []
        if not p_val:
            missing_in.append("Primary Doc")
        if supp and not s_val:
            missing_in.append("Supporting Doc")
        if mrz and not m_val:
            missing_in.append("MRZ Data")

        if missing_in and len(missing_in) < len(sources):
            missing_fields.append({
                "field": field_name_clean,
                "missing_in": missing_in
            })

    # Calculate Consistency Score (0.0 to 100.0)
    consistency_score = 100.0
    if mismatch_count > 0:
        consistency_score -= (mismatch_count * 25.0)
    if missing_fields:
        consistency_score -= (len(missing_fields) * 5.0)

    consistency_score = min(100.0, max(0.0, consistency_score))

    summary = (
        f"Cross-document consistency check completed. {len(matching_fields)} matching field pairs, "
        f"{mismatch_count} mismatches detected."
    )

    return {
        "consistency_score": round(consistency_score, 1),
        "matching_fields": matching_fields,
        "mismatched_fields": mismatched_fields,
        "missing_fields": missing_fields,
        "summary_message": summary
    }
