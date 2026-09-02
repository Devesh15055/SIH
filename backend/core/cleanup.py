"""
Temporary Files & Workspaces Cleanup Utility
Ensures temporary upload bytes and ELA preview images are cleaned after processing.
"""

import os
import time

TEMP_DIR = "C:/Users/Hp/OneDrive/Desktop/SIH2/temp"

def cleanup_temp_files(max_age_seconds: int = 3600):
    """
    Remove temporary files older than max_age_seconds from temp/.
    Always preserves .gitkeep.
    """
    if not os.path.exists(TEMP_DIR):
        return

    now = time.time()
    cleaned_count = 0

    for filename in os.listdir(TEMP_DIR):
        if filename == ".gitkeep":
            continue

        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.isfile(file_path):
            try:
                file_age = now - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    cleaned_count += 1
            except Exception as e:
                print(f"Error cleaning temp file {file_path}: {str(e)}")

    return cleaned_count
