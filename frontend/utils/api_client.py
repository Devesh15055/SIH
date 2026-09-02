"""
Decoupled HTTP API Client for Frontend-Backend Communication
"""

import requests
from typing import Dict, Any, Optional

BACKEND_BASE_URL = "http://localhost:8000"

def check_backend_health() -> bool:
    try:
        resp = requests.get(f"{BACKEND_BASE_URL}/health", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False

def submit_screening_request(primary_file_bytes: bytes, primary_filename: str, selfie_bytes: Optional[bytes] = None, selfie_filename: Optional[str] = None) -> Dict[str, Any]:
    try:
        files = {
            "primary_document": (primary_filename, primary_file_bytes, "image/jpeg")
        }
        if selfie_bytes and selfie_filename:
            files["selfie"] = (selfie_filename, selfie_bytes, "image/jpeg")

        resp = requests.post(f"{BACKEND_BASE_URL}/api/v1/screen", files=files, timeout=30)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        else:
            return {"success": False, "error": f"API Error ({resp.status_code}): {resp.text}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to connect to backend API: {str(e)}"}
