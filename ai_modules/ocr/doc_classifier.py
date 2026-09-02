"""
Automatic Identity Document Type Classifier Engine
Classifies uploaded documents into Passport, Aadhaar, PAN Card, Driving License, Voter ID, or Generic ID.
"""

import re
from typing import Dict, Any, List

DOC_RULES = {
    "PASSPORT": {
        "label": "Passport (ICAO 9303)",
        "keywords": ["PASSPORT", "REPUBLIC OF INDIA", "TYPE P", "COUNTRY CODE"],
        "regex": r"\b[A-Z][0-9]{7}\b"
    },
    "AADHAAR": {
        "label": "Aadhaar Card (UIDAI)",
        "keywords": ["GOVERNMENT OF INDIA", "UNIQUE IDENTIFICATION", "AADHAAR", "MALE", "FEMALE", "DOB"],
        "regex": r"\b\d{4}\s?\d{4}\s?\d{4}\b"
    },
    "PAN_CARD": {
        "label": "PAN Card (Income Tax Dept)",
        "keywords": ["INCOME TAX DEPARTMENT", "PERMANENT ACCOUNT NUMBER", "GOVT OF INDIA"],
        "regex": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
    },
    "DRIVING_LICENSE": {
        "label": "Driving License",
        "keywords": ["DRIVING LICENCE", "DRIVING LICENSE", "TRANSPORT DEPARTMENT", "UNION OF INDIA"],
        "regex": r"\b[A-Z]{2}[0-9]{13}\b"
    },
    "VOTER_ID": {
        "label": "Voter ID Card (ECI)",
        "keywords": ["ELECTION COMMISSION OF INDIA", "ELECTORAL PHOTO IDENTITY CARD", "EPIC"],
        "regex": r"\b[A-Z]{3}[0-9]{7}\b"
    }
}

def classify_document(raw_text: str, mrz_detected: bool = False) -> Dict[str, Any]:
    """
    Classify document type based on OCR text keywords, regex matchers, and MRZ presence.
    """
    text_upper = raw_text.upper() if raw_text else ""
    matched_type = "GENERIC_ID"
    matched_label = "Generic Identity Document"
    highest_score = 0
    matched_keywords = []

    if mrz_detected or "P<" in text_upper or "PASSPORT" in text_upper:
        return {
            "document_type": "PASSPORT",
            "document_label": "Passport (ICAO 9303)",
            "confidence": 95.0,
            "detected_keywords": ["MRZ Line / Passport Header"]
        }

    for doc_type, rule in DOC_RULES.items():
        score = 0
        found_kw = []
        for kw in rule["keywords"]:
            if kw in text_upper:
                score += 25
                found_kw.append(kw)
        
        if re.search(rule["regex"], text_upper):
            score += 40
            found_kw.append("ID Number Format Match")

        if score > highest_score:
            highest_score = score
            matched_type = doc_type
            matched_label = rule["label"]
            matched_keywords = found_kw

    confidence = min(95.0, max(50.0, float(highest_score)))

    return {
        "document_type": matched_type,
        "document_label": matched_label,
        "confidence": confidence if highest_score > 0 else 50.0,
        "detected_keywords": matched_keywords
    }
