"""Unit tests for PDF Report Generator"""
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reports import generate_pdf_report, get_pdf_bytes

class TestPDFGenerator(unittest.TestCase):
    def setUp(self):
        self.sample_result = {
            "screening_id": "SIH2-TESTPDF1",
            "overall_risk_score": 15.0,
            "decision": "APPROVED",
            "ocr_result": {"confidence": 92.0, "fields": {"full_name": "TEST USER", "document_number": "A1234567"}},
            "mrz_result": {"mrz_detected": True, "status_message": "MRZ valid"},
            "forensics_result": {"risk_level": "LOW", "tampering_risk_score": 10.0, "indicators": []},
            "face_verification_result": {"status": "MATCH", "similarity_score": 90.0},
            "selfie_authenticity_result": {"authenticity_score": 95.0, "screening_label": "Prototype AI-assisted screening"},
            "consistency_result": {"consistency_score": 100.0},
            "risk_scoring_result": {"risk_classification": "LOW RISK", "human_explanation": ["All checks passed."]}
        }

    def test_pdf_generation(self):
        pdf_path = generate_pdf_report(self.sample_result)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertTrue(pdf_path.endswith(".pdf"))
        
        pdf_bytes = get_pdf_bytes(pdf_path)
        self.assertTrue(len(pdf_bytes) > 0)

if __name__ == "__main__":
    unittest.main()
