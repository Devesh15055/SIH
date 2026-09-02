"""
Selfie Authenticity & Anti-Spoofing Screening Module (Prototype AI-Assisted Screening)
Provides modular interface for evaluating face presence, quality anomalies, high-pass noise residuals,
and JPEG compression artifacts.
"""

import cv2
import numpy as np
import os
from typing import Dict, List, Any, Optional

def detect_deepfake_artifacts(image_input: Any) -> Dict[str, Any]:
    """
    Perform prototype AI-assisted selfie authenticity screening.
    
    Disclaimer: Prototype AI-assisted screening: Heuristic analysis for early artifact detection.
    Not a certified anti-spoofing biometrics engine.
    """
    disclaimer = "Prototype AI-assisted screening: Heuristic analysis for early artifact detection. Not a certified anti-spoofing biometrics engine."

    def load_img(inp):
        if isinstance(inp, bytes):
            nparr = np.frombuffer(inp, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(inp, str) and os.path.exists(inp):
            return cv2.imread(inp)
        elif isinstance(inp, np.ndarray):
            return inp
        return None

    img = load_img(image_input)

    if img is None:
        return {
            "face_detected": False,
            "authenticity_score": 0.0,
            "is_suspicious": False,
            "screening_label": "Prototype AI-assisted screening",
            "detected_indicators": ["No valid selfie image supplied."],
            "quality_metrics": {
                "blur_variance": 0.0,
                "exposure_level": "Unknown",
                "compression_artifacts": "Unknown"
            },
            "disclaimer": disclaimer
        }

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    h, w = gray.shape[:2]

    detected_indicators = []
    suspicious = False
    authenticity_score = 90.0

    # 1. Blur Variance (High-pass frequency residual check)
    blur_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if blur_var < 35.0:
        detected_indicators.append(f"High blur detected (variance {blur_var:.1f}). Possible digital smoothing or re-photo artifact.")
        authenticity_score -= 20.0
        suspicious = True

    # 2. Exposure & Over-saturation check
    mean_bright = float(np.mean(gray))
    exposure_str = "Optimal"
    if mean_bright < 35.0 or mean_bright > 225.0:
        exposure_str = "Suboptimal"
        detected_indicators.append("Extreme exposure anomaly detected.")
        authenticity_score -= 10.0

    # 3. High-Pass Noise Residual Analysis for Smoothing/Generative Artifacts
    blur_img = cv2.GaussianBlur(gray, (5, 5), 0)
    noise_residual = cv2.absdiff(gray, blur_img)
    mean_residual = float(np.mean(noise_residual))

    if mean_residual < 2.0:
        detected_indicators.append("Unnaturally smooth noise texture (potential AI generation or heavy beauty filter).")
        authenticity_score -= 15.0
        suspicious = True

    # 4. Face presence check using OpenCV
    CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_detected = True
    if os.path.exists(CASCADE_PATH):
        cascade = cv2.CascadeClassifier(CASCADE_PATH)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)
        face_detected = len(faces) > 0

    if not face_detected:
        detected_indicators.append("No clear frontal face structure detected in selfie.")
        authenticity_score -= 30.0

    authenticity_score = max(0.0, min(100.0, authenticity_score))

    return {
        "face_detected": face_detected,
        "authenticity_score": round(authenticity_score, 1),
        "is_suspicious": suspicious or authenticity_score < 60.0,
        "screening_label": "Prototype AI-assisted screening",
        "detected_indicators": detected_indicators,
        "quality_metrics": {
            "blur_variance": round(blur_var, 1),
            "exposure_level": exposure_str,
            "noise_residual_score": round(mean_residual, 2)
        },
        "disclaimer": disclaimer
    }
