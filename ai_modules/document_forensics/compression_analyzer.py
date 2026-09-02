"""
JPEG Compression & Block Artifact Analysis Component
Analyzes 8x8 block grid boundary discontinuities and noise variance.
"""

import cv2
import numpy as np
import io
import os
from typing import Dict, Any, List

def analyze_compression(image_input: Any) -> Dict[str, Any]:
    """
    Inspect JPEG 8x8 block grid discontinuity and localized edge sharpness variance.
    """
    warnings = []
    indicators = []

    def load_cv2(inp):
        if isinstance(inp, bytes):
            nparr = np.frombuffer(inp, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(inp, str) and os.path.exists(inp):
            return cv2.imread(inp)
        elif isinstance(inp, np.ndarray):
            return inp
        return None

    img = load_cv2(image_input)
    if img is None:
        return {
            "block_grid_discontinuity": 0.0,
            "indicators": [],
            "warnings": ["Failed to load image for compression analysis."]
        }

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    h, w = gray.shape

    # 8x8 JPEG Block boundary difference calculation
    if h >= 16 and w >= 16:
        row1 = gray[7::8, :]
        row2 = gray[8::8, :]
        min_h = min(row1.shape[0], row2.shape[0])
        block_diff_h = np.abs(row1[:min_h, :].astype(np.int16) - row2[:min_h, :].astype(np.int16))

        col1 = gray[:, 7::8]
        col2 = gray[:, 8::8]
        min_w = min(col1.shape[1], col2.shape[1])
        block_diff_v = np.abs(col1[:, :min_w].astype(np.int16) - col2[:, :min_w].astype(np.int16))
        
        block_grid_score = float(np.mean(block_diff_h) + np.mean(block_diff_v)) / 2.0
    else:
        block_grid_score = 0.0

    if block_grid_score > 25.0:
        indicators.append(f"High JPEG 8x8 block grid boundary discontinuity (score: {block_grid_score:.1f}). Possible double JPEG compression.")

    return {
        "block_grid_discontinuity": round(block_grid_score, 2),
        "indicators": indicators,
        "warnings": warnings
    }
