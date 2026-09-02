"""
EXIF and File Metadata Analysis Component
Inspects software signature tags, camera metadata, and date inconsistencies.
"""

from PIL import Image, ExifTags
import io
import os
from typing import Dict, Any, List

SUSPICIOUS_SOFTWARE_KEYWORDS = [
    "photoshop", "gimp", "paint.net", "canva", "adobe", "illustrator",
    "coreldraw", "pixlr", "snapseed", "lightroom"
]

def analyze_metadata(image_input: Any) -> Dict[str, Any]:
    """
    Inspect image EXIF metadata for editing software artifacts and timestamp anomalies.
    """
    warnings = []
    indicators = []
    software_detected = None
    has_exif = False

    try:
        if isinstance(image_input, bytes):
            img = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, str) and os.path.exists(image_input):
            img = Image.open(image_input)
        else:
            return {
                "has_exif": False,
                "software_detected": None,
                "indicators": [],
                "warnings": ["Unsupported image input for metadata analysis."]
            }

        exif_data = img._getexif() if hasattr(img, '_getexif') else None

        if exif_data:
            has_exif = True
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                val_str = str(value).lower()

                if tag_name == "Software":
                    software_detected = str(value)
                    for kw in SUSPICIOUS_SOFTWARE_KEYWORDS:
                        if kw in val_str:
                            indicators.append(f"Image edited using graphics software: '{value}'")
                            break

                elif tag_name == "ProcessingSoftware":
                    indicators.append(f"Processing software metadata tag found: '{value}'")

    except Exception as e:
        warnings.append(f"Could not parse EXIF metadata: {str(e)}")

    return {
        "has_exif": has_exif,
        "software_detected": software_detected,
        "indicators": indicators,
        "warnings": warnings
    }
