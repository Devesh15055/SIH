"""Unit tests for Explainable Risk Scoring Engine"""
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_modules.risk_scoring import calculate_explainable_risk_score, DEFAULT_WEIGHTS

class TestExplainableRiskScoring(unittest.TestCase):
    def test_low_risk_scenario(self):
        res = calculate_explainable_risk_score(
            face_result={"status": "MATCH", "similarity_score": 92.0},
            forensics_result={"tampering_risk_score": 10.0, "risk_level": "LOW"},
            consistency_result={"consistency_score": 100.0, "mismatched_fields": []},
            mrz_result={"mrz_detected": True, "validation_errors": []},
            ocr_result={"confidence": 95.0},
            selfie_result={"authenticity_score": 95.0, "is_suspicious": False}
        )
        self.assertLessEqual(res["final_risk_score"], 25.0)
        self.assertEqual(res["risk_classification"], "LOW RISK")
        self.assertEqual(res["recommended_decision"], "APPROVED")

    def test_high_risk_scenario(self):
        res = calculate_explainable_risk_score(
            face_result={"status": "MISMATCH", "similarity_score": 20.0},
            forensics_result={"tampering_risk_score": 80.0, "risk_level": "HIGH"},
            consistency_result={"consistency_score": 40.0, "mismatched_fields": [{"field": "Full Name"}]},
            mrz_result={"mrz_detected": True, "validation_errors": ["Checksum mismatch"]},
            ocr_result={"confidence": 40.0},
            selfie_result={"authenticity_score": 30.0, "is_suspicious": True}
        )
        self.assertGreater(res["final_risk_score"], 50.0)
        self.assertIn(res["risk_classification"], ["HIGH RISK", "CRITICAL RISK"])
        self.assertEqual(res["recommended_decision"], "REJECTED")
        self.assertTrue(len(res["human_explanation"]) > 0)

    def test_custom_weights(self):
        custom_w = {"face_verification": 0.50, "document_forensics": 0.50}
        res = calculate_explainable_risk_score(
            face_result={"status": "MATCH"},
            forensics_result={"tampering_risk_score": 10.0},
            consistency_result={}, mrz_result={}, ocr_result={}, selfie_result={},
            custom_weights=custom_w
        )
        self.assertIn("face_verification", res["configured_weights"])

if __name__ == "__main__":
    unittest.main()
