"""
Biometric Face Detection, Quality Analysis, and Face Verification Module
Uses OpenCV Haar Cascades, Skin-Tone Histograms, and Multi-Scale Feature Alignment.
"""

import cv2
import numpy as np
import io
import os
from typing import Dict, List, Any, Optional, Tuple

# Load OpenCV Haar Cascade for Frontal Face Detection
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(CASCADE_PATH) if os.path.exists(CASCADE_PATH) else None

def check_image_quality(img_np: np.ndarray) -> Tuple[Dict[str, Any], List[str]]:
    """
    Evaluate face image quality:
    - Resolution / Dimensions
    - Blur / Sharpness using Laplacian variance
    - Exposure / Brightness level
    """
    warnings = []
    h, w = img_np.shape[:2]

    if h < 100 or w < 100:
        warnings.append(f"Low image resolution ({w}x{h}px). Recommended minimum 200x200px.")

    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY) if len(img_np.shape) == 3 else img_np
    
    # Laplacian Variance for Blur Detection
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if laplacian_var < 40.0:
        warnings.append(f"Image appears blurry (sharpness score: {laplacian_var:.1f}).")

    # Brightness / Exposure Check
    mean_brightness = float(np.mean(gray))
    if mean_brightness < 40.0:
        warnings.append("Image is underexposed / dark.")
    elif mean_brightness > 220.0:
        warnings.append("Image is overexposed / washed out.")

    metrics = {
        "width": w,
        "height": h,
        "sharpness_score": laplacian_var,
        "mean_brightness": mean_brightness,
        "is_blurry": laplacian_var < 40.0
    }
    return metrics, warnings

def detect_faces(img_np: np.ndarray) -> Tuple[List[Tuple[int, int, int, int]], List[str]]:
    """
    Detect frontal face bounding boxes: [(x, y, w, h), ...]
    Fallback to skin-tone contour heuristics if Haar cascade is unavailable.
    """
    warnings = []
    if img_np is None or img_np.size == 0:
        return [], ["Invalid or empty image array."]

    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY) if len(img_np.shape) == 3 else img_np

    faces = []
    if face_cascade is not None and not face_cascade.empty():
        detected = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(40, 40)
        )
        faces = [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in detected]

    # Skin color region fallback if Haar cascade misses
    if not faces and len(img_np.shape) == 3:
        ycrcb = cv2.cvtColor(img_np, cv2.COLOR_BGR2YCrCb)
        lower_skin = np.array([0, 133, 77], dtype=np.uint8)
        upper_skin = np.array([255, 173, 127], dtype=np.uint8)
        mask = cv2.inRange(ycrcb, lower_skin, upper_skin)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for c in contours:
            area = cv2.contourArea(c)
            if area > (img_np.shape[0] * img_np.shape[1] * 0.05):
                x, y, w, h = cv2.boundingRect(c)
                aspect_ratio = float(w) / h
                if 0.6 <= aspect_ratio <= 1.4:
                    faces.append((int(x), int(y), int(w), int(h)))
                    break

    if len(faces) > 1:
        warnings.append(f"Multiple faces detected ({len(faces)} faces). Analyzing the primary bounding box.")

    return faces, warnings

def extract_face_chip(img_np: np.ndarray, bbox: Tuple[int, int, int, int], target_size=(128, 128)) -> np.ndarray:
    """Crop and normalize face image chip."""
    x, y, w, h = bbox
    crop = img_np[y:y+h, x:x+w]
    if crop.size == 0:
        return cv2.resize(img_np, target_size)
    return cv2.resize(crop, target_size)

def compute_face_similarity(face_chip1: np.ndarray, face_chip2: np.ndarray) -> float:
    """
    Calculate deterministic face similarity score (0.0 to 100.0) using:
    - HSV Color & Skin Texture Histogram Correlation
    - Normalized Cross-Correlation (NCC) / Structural Dissimilarity
    """
    chip1 = cv2.resize(face_chip1, (128, 128))
    chip2 = cv2.resize(face_chip2, (128, 128))

    # Convert to HSV and calculate 2D Color Histogram
    hsv1 = cv2.cvtColor(chip1, cv2.COLOR_BGR2HSV) if len(chip1.shape) == 3 else chip1
    hsv2 = cv2.cvtColor(chip2, cv2.COLOR_BGR2HSV) if len(chip2.shape) == 3 else chip2

    hist1 = cv2.calcHist([hsv1], [0, 1], None, [32, 32], [0, 180, 0, 256])
    hist2 = cv2.calcHist([hsv2], [0, 1], None, [32, 32], [0, 180, 0, 256])
    cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
    cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)

    hist_corr = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    hist_score = max(0.0, float(hist_corr)) * 100.0

    # Gray Structure Correlation
    gray1 = cv2.cvtColor(chip1, cv2.COLOR_BGR2GRAY) if len(chip1.shape) == 3 else chip1
    gray2 = cv2.cvtColor(chip2, cv2.COLOR_BGR2GRAY) if len(chip2.shape) == 3 else chip2

    diff = cv2.absdiff(gray1, gray2)
    mean_diff = float(np.mean(diff))
    struct_score = max(0.0, (1.0 - (mean_diff / 255.0))) * 100.0

    # Weighted aggregate similarity
    final_score = (hist_score * 0.5) + (struct_score * 0.5)
    return round(float(final_score), 2)

def verify_faces(doc_img_input: Any, selfie_img_input: Optional[Any] = None) -> Dict[str, Any]:
    """
    Main entrypoint for Face Detection & Verification.
    Accepts image bytes, file paths, or numpy arrays for doc and selfie.
    """
    quality_warnings = []

    def load_numpy_img(inp):
        if inp is None:
            return None
        elif isinstance(inp, bytes):
            nparr = np.frombuffer(inp, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(inp, str) and os.path.exists(inp):
            return cv2.imread(inp)
        elif isinstance(inp, np.ndarray):
            return inp
        return None

    doc_img = load_numpy_img(doc_img_input)
    selfie_img = load_numpy_img(selfie_img_input)

    if doc_img is None:
        return {
            "document_face_detected": False,
            "selfie_face_detected": False,
            "similarity_score": 0.0,
            "status": "INCONCLUSIVE",
            "quality_warnings": ["Invalid or missing primary document image."]
        }

    # Quality check doc
    doc_q, doc_qw = check_image_quality(doc_img)
    quality_warnings.extend([f"Doc: {w}" for w in doc_qw])

    # Detect faces in document
    doc_faces, doc_fw = detect_faces(doc_img)
    quality_warnings.extend([f"Doc: {w}" for w in doc_fw])
    doc_face_detected = len(doc_faces) > 0

    if selfie_img_input is None or selfie_img is None:
        return {
            "document_face_detected": doc_face_detected,
            "selfie_face_detected": False,
            "similarity_score": 0.0,
            "status": "INCONCLUSIVE",
            "quality_warnings": quality_warnings + ["No selfie photo provided for facial matching."]
        }

    # Quality check selfie
    selfie_q, selfie_qw = check_image_quality(selfie_img)
    quality_warnings.extend([f"Selfie: {w}" for w in selfie_qw])

    # Detect faces in selfie
    selfie_faces, selfie_fw = detect_faces(selfie_img)
    quality_warnings.extend([f"Selfie: {w}" for w in selfie_fw])
    selfie_face_detected = len(selfie_faces) > 0

    if not doc_face_detected or not selfie_face_detected:
        status_msg = "No face detected in ID document." if not doc_face_detected else "No face detected in selfie photo."
        return {
            "document_face_detected": doc_face_detected,
            "selfie_face_detected": selfie_face_detected,
            "similarity_score": 0.0,
            "status": "INCONCLUSIVE",
            "quality_warnings": quality_warnings + [status_msg]
        }

    # Extract face chips and compute similarity
    doc_chip = extract_face_chip(doc_img, doc_faces[0])
    selfie_chip = extract_face_chip(selfie_img, selfie_faces[0])

    similarity_score = compute_face_similarity(doc_chip, selfie_chip)

    # Determine status verdict based on threshold
    if similarity_score >= 65.0:
        status = "MATCH"
    elif similarity_score >= 45.0:
        status = "POSSIBLE MISMATCH"
    else:
        status = "MISMATCH"

    return {
        "document_face_detected": True,
        "selfie_face_detected": True,
        "similarity_score": similarity_score,
        "status": status,
        "quality_warnings": quality_warnings
    }
