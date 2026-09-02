"""
Error Level Analysis (ELA) Component
Detects re-compression discrepancies across image regions.
Generates an intermediate ELA visual image saved temporarily in temp/.
"""

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import io
import os
import uuid
from typing import Dict, Any, Tuple, Optional

def perform_ela(image_input: Any, scale: float = 15.0, quality: int = 90) -> Dict[str, Any]:
    """
    Perform Error Level Analysis by comparing original image with JPEG re-compressed version.
    Saves temporary ELA visual preview image in temp/.
    """
    warnings = []
    ela_path = None

    def load_pil(inp):
        try:
            if isinstance(inp, bytes):
                return Image.open(io.BytesIO(inp)).convert("RGB")
            elif isinstance(inp, str) and os.path.exists(inp):
                return Image.open(inp).convert("RGB")
            elif isinstance(inp, np.ndarray):
                return Image.fromarray(cv2.cvtColor(inp, cv2.COLOR_BGR2RGB))
        except Exception:
            return None
        return None

    orig_img = load_pil(image_input)
    if orig_img is None:
        return {
            "ela_mean_error": 0.0,
            "ela_max_error": 0.0,
            "suspicious_patch_count": 0,
            "ela_image_path": None,
            "warnings": ["Failed to load image for Error Level Analysis."]
        }

    # Re-compress in memory at specified JPEG quality
    buffer = io.BytesIO()
    orig_img.save(buffer, 'JPEG', quality=quality)
    buffer.seek(0)
    compressed_img = Image.open(buffer)

    # Compute absolute difference
    ela_img = ImageChops.difference(orig_img, compressed_img)
    
    # Scale difference for visual inspection
    extrema = ela_img.getextrema()
    max_diff = max([ex[1] for ex in extrema]) if extrema else 1
    if max_diff == 0:
        max_diff = 1
    scale_factor = 255.0 / max_diff if max_diff < 20 else scale
    
    enhancer = ImageEnhance.Brightness(ela_img)
    ela_enhanced = enhancer.enhance(scale_factor)

    # Save intermediate ELA preview image in temp/
    temp_dir = "C:/Users/Hp/OneDrive/Desktop/SIH2/temp"
    os.makedirs(temp_dir, exist_ok=True)
    ela_filename = f"ela_{uuid.uuid4().hex[:8]}.jpg"
    ela_path = os.path.join(temp_dir, ela_filename)
    ela_enhanced.save(ela_path, "JPEG")

    # Compute numerical ELA error statistics
    ela_np = np.array(ela_img)
    mean_error = float(np.mean(ela_np))
    max_error = float(np.max(ela_np))
    std_error = float(np.std(ela_np))

    # Detect high-variance ELA patches (local editing indicators)
    gray_ela = cv2.cvtColor(ela_np, cv2.COLOR_RGB2GRAY) if len(ela_np.shape) == 3 else ela_np
    _, patch_thresh = cv2.threshold(gray_ela, int(mean_error + 2.5 * std_error + 5), 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(patch_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    suspicious_patches = len([c for c in contours if cv2.contourArea(c) > 20])

    if suspicious_patches > 5:
        warnings.append(f"Detected {suspicious_patches} localized high-contrast ELA anomaly patches.")

    return {
        "ela_mean_error": round(mean_error, 2),
        "ela_max_error": round(max_error, 2),
        "ela_std_error": round(std_error, 2),
        "suspicious_patch_count": suspicious_patches,
        "ela_image_path": ela_path,
        "warnings": warnings
    }
