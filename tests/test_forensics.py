"""Unit tests for Document Forensics Module"""
import unittest
import numpy as np
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_modules.document_forensics import analyze_document_forensics, perform_ela, analyze_metadata, analyze_compression

class TestDocumentForensics(unittest.TestCase):
    def setUp(self):
        # Create synthetic test image
        self.blank = np.ones((200, 200, 3), dtype=np.uint8) * 180

    def test_perform_ela(self):
        res = perform_ela(self.blank)
        self.assertIn("ela_mean_error", res)
        self.assertIn("suspicious_patch_count", res)
        self.assertIsNotNone(res["ela_image_path"])
        if res["ela_image_path"]:
            self.assertTrue(os.path.exists(res["ela_image_path"]))

    def test_metadata_analysis(self):
        res = analyze_metadata(self.blank)
        self.assertIn("has_exif", res)
        self.assertIn("indicators", res)

    def test_compression_analysis(self):
        res = analyze_compression(self.blank)
        self.assertIn("block_grid_discontinuity", res)

    def test_forensics_engine(self):
        res = analyze_document_forensics(self.blank)
        self.assertIn("tampering_risk_score", res)
        self.assertIn(res["risk_level"], ["LOW", "MEDIUM", "HIGH"])
        self.assertTrue(isinstance(res["indicators"], list))
        self.assertTrue(isinstance(res["analysis_warnings"], list))

if __name__ == "__main__":
    unittest.main()
