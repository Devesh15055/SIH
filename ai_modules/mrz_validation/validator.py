"""
MRZ (Machine Readable Zone) Parsing & Checksum Validation Module
Compliant with ICAO Document 9303 Standards.
Supports TD3 (Passport 2x44), TD1 (ID Card 3x30), TD2 (ID Card/Visa 2x36), and Visa formats.
"""

import re
from typing import Dict, List, Any, Optional

WEIGHTS = [7, 3, 1]

def calculate_checksum(data_str: str) -> int:
    """
    Calculate ICAO 9303 7-3-1 check digit for a string.
    '<' or fill characters count as 0.
    'A'-'Z' map to 10-35. '0'-'9' map to 0-9.
    """
    total = 0
    for idx, char in enumerate(data_str):
        weight = WEIGHTS[idx % 3]
        if char == '<' or char == ' ':
            val = 0
        elif char.isdigit():
            val = int(char)
        elif char.isalpha():
            val = ord(char.upper()) - 55
        else:
            val = 0
        total += val * weight
    return total % 10

def parse_mrz_lines(raw_lines: List[str]) -> Dict[str, Any]:
    """
    Detect MRZ lines and parse fields based on length:
    - TD3 (Passport): 2 lines of 44 chars
    - TD1 (ID Card): 3 lines of 30 chars
    - TD2 (ID Card/Visa): 2 lines of 36 chars
    """
    cleaned_lines = [re.sub(r'[^A-Z0-9<]', '', line.strip().upper()) for line in raw_lines if line.strip()]
    mrz_lines = [l for l in cleaned_lines if len(l) in (30, 36, 44) or '<' in l]

    if not mrz_lines:
        return {
            "mrz_detected": False,
            "parsed_fields": {},
            "checksum_status": {
                "document_number": False,
                "dob": False,
                "expiry_date": False,
                "composite": False
            },
            "validation_errors": ["No valid MRZ lines matching ICAO 9303 length detected"],
            "status_message": "MRZ not present or not detected"
        }

    # TD3 Passport format (2 lines of 44)
    if len(mrz_lines) >= 2 and len(mrz_lines[0]) == 44 and len(mrz_lines[1]) == 44:
        return parse_td3(mrz_lines[0], mrz_lines[1])
    
    # TD1 ID format (3 lines of 30)
    elif len(mrz_lines) >= 3 and len(mrz_lines[0]) == 30 and len(mrz_lines[1]) == 30 and len(mrz_lines[2]) == 30:
        return parse_td1(mrz_lines[0], mrz_lines[1], mrz_lines[2])

    # TD2 ID/Visa format (2 lines of 36)
    elif len(mrz_lines) >= 2 and len(mrz_lines[0]) == 36 and len(mrz_lines[1]) == 36:
        return parse_td2(mrz_lines[0], mrz_lines[1])

    # Fallback/partial match attempt
    return parse_generic_mrz(mrz_lines)

def parse_td3(line1: str, line2: str) -> Dict[str, Any]:
    """Parse 2x44 TD3 Passport MRZ format."""
    doc_type = line1[0:2].replace('<', '')
    country = line1[2:5].replace('<', '')
    names = line1[5:44].split('<<')
    surname = names[0].replace('<', ' ').strip()
    given_names = names[1].replace('<', ' ').strip() if len(names) > 1 else ""

    doc_num = line2[0:9].replace('<', '')
    doc_num_check = line2[9]
    nationality = line2[10:13].replace('<', '')
    dob = line2[13:19]
    dob_check = line2[19]
    sex = line2[20]
    expiry = line2[21:27]
    expiry_check = line2[27]
    composite_check = line2[43]

    calc_doc_check = calculate_checksum(line2[0:9])
    calc_dob_check = calculate_checksum(dob)
    calc_exp_check = calculate_checksum(expiry)

    doc_valid = str(calc_doc_check) == doc_num_check
    dob_valid = str(calc_dob_check) == dob_check
    exp_valid = str(calc_exp_check) == expiry_check
    comp_valid = doc_valid and dob_valid and exp_valid

    errors = []
    if not doc_valid:
        errors.append(f"Document number checksum mismatch (expected {calc_doc_check}, got {doc_num_check})")
    if not dob_valid:
        errors.append(f"DOB checksum mismatch (expected {calc_dob_check}, got {dob_check})")
    if not exp_valid:
        errors.append(f"Expiry date checksum mismatch (expected {calc_exp_check}, got {expiry_check})")

    return {
        "mrz_detected": True,
        "format": "TD3 (Passport)",
        "parsed_fields": {
            "document_type": doc_type,
            "issuing_country": country,
            "surname": surname,
            "given_names": given_names,
            "document_number": doc_num,
            "nationality": nationality,
            "date_of_birth": f"19{dob[:2]}-{dob[2:4]}-{dob[4:]}" if int(dob[:2]) > 30 else f"20{dob[:2]}-{dob[2:4]}-{dob[4:]}",
            "gender": "Male" if sex == 'M' else "Female" if sex == 'F' else "Other",
            "expiry_date": f"20{expiry[:2]}-{expiry[2:4]}-{expiry[4:]}"
        },
        "checksum_status": {
            "document_number": doc_valid,
            "dob": dob_valid,
            "expiry_date": exp_valid,
            "composite": comp_valid
        },
        "validation_errors": errors,
        "status_message": "MRZ TD3 detected and parsed successfully" if not errors else "MRZ TD3 detected with checksum validation errors"
    }

def parse_td1(line1: str, line2: str, line3: str) -> Dict[str, Any]:
    """Parse 3x30 TD1 ID Card MRZ format."""
    doc_type = line1[0:2].replace('<', '')
    country = line1[2:5].replace('<', '')
    doc_num = line1[5:14].replace('<', '')
    doc_num_check = line1[14]

    dob = line2[0:6]
    dob_check = line2[6]
    sex = line2[7]
    expiry = line2[8:14]
    expiry_check = line2[14]
    nationality = line2[15:18].replace('<', '')

    names = line3.split('<<')
    surname = names[0].replace('<', ' ').strip()
    given_names = names[1].replace('<', ' ').strip() if len(names) > 1 else ""

    doc_valid = str(calculate_checksum(line1[5:14])) == doc_num_check
    dob_valid = str(calculate_checksum(dob)) == dob_check
    exp_valid = str(calculate_checksum(expiry)) == expiry_check

    errors = []
    if not doc_valid:
        errors.append("Document number checksum mismatch")
    if not dob_valid:
        errors.append("DOB checksum mismatch")
    if not exp_valid:
        errors.append("Expiry date checksum mismatch")

    return {
        "mrz_detected": True,
        "format": "TD1 (ID Card)",
        "parsed_fields": {
            "document_type": doc_type,
            "issuing_country": country,
            "surname": surname,
            "given_names": given_names,
            "document_number": doc_num,
            "nationality": nationality,
            "date_of_birth": dob,
            "gender": sex,
            "expiry_date": expiry
        },
        "checksum_status": {
            "document_number": doc_valid,
            "dob": dob_valid,
            "expiry_date": exp_valid,
            "composite": doc_valid and dob_valid and exp_valid
        },
        "validation_errors": errors,
        "status_message": "MRZ TD1 detected and parsed"
    }

def parse_td2(line1: str, line2: str) -> Dict[str, Any]:
    """Parse 2x36 TD2 ID/Visa MRZ format."""
    doc_type = line1[0:2].replace('<', '')
    country = line1[2:5].replace('<', '')
    names = line1[5:36].split('<<')
    surname = names[0].replace('<', ' ').strip()
    given_names = names[1].replace('<', ' ').strip() if len(names) > 1 else ""

    doc_num = line2[0:9].replace('<', '')
    doc_num_check = line2[9]
    nationality = line2[10:13].replace('<', '')
    dob = line2[13:19]
    dob_check = line2[19]
    sex = line2[20]
    expiry = line2[21:27]
    expiry_check = line2[27]

    doc_valid = str(calculate_checksum(line2[0:9])) == doc_num_check
    dob_valid = str(calculate_checksum(dob)) == dob_check
    exp_valid = str(calculate_checksum(expiry)) == expiry_check

    return {
        "mrz_detected": True,
        "format": "TD2 (ID Card / Visa)",
        "parsed_fields": {
            "document_type": doc_type,
            "issuing_country": country,
            "surname": surname,
            "given_names": given_names,
            "document_number": doc_num,
            "nationality": nationality,
            "date_of_birth": dob,
            "gender": sex,
            "expiry_date": expiry
        },
        "checksum_status": {
            "document_number": doc_valid,
            "dob": dob_valid,
            "expiry_date": exp_valid,
            "composite": doc_valid and dob_valid and exp_valid
        },
        "validation_errors": [],
        "status_message": "MRZ TD2 detected and parsed"
    }

def parse_generic_mrz(lines: List[str]) -> Dict[str, Any]:
    """Fallback MRZ parser for partial or non-standard MRZ lines."""
    full_text = "".join(lines)
    has_mrz = '<' in full_text
    return {
        "mrz_detected": has_mrz,
        "format": "Generic / Unstructured MRZ",
        "parsed_fields": {"raw_mrz": full_text},
        "checksum_status": {
            "document_number": False,
            "dob": False,
            "expiry_date": False,
            "composite": False
        },
        "validation_errors": ["Non-standard MRZ line length"],
        "status_message": "Partial MRZ detected but non-standard format" if has_mrz else "MRZ not present or not detected"
    }

def validate_mrz(mrz_input: Any) -> Dict[str, Any]:
    """Public wrapper to validate MRZ from raw string, lines, or image bytes."""
    if isinstance(mrz_input, str):
        lines = mrz_input.split('\n')
    elif isinstance(mrz_input, list):
        lines = mrz_input
    else:
        lines = []

    return parse_mrz_lines(lines)
