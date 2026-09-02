"""Unit tests for Cross-Document Data Consistency Module"""
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_modules.risk_scoring import check_cross_document_consistency

class TestDataConsistency(unittest.TestCase):
    def test_matching_fields(self):
        p = {"full_name": "RAHUL SHARMA", "date_of_birth": "12/05/1992", "document_number": "1234 5678 9012"}
        m = {"full_name": "RAHUL SHARMA", "date_of_birth": "12/05/1992", "document_number": "123456789012"}
        res = check_cross_document_consistency(p, mrz_fields=m)
        self.assertGreaterEqual(res["consistency_score"], 90.0)
        self.assertEqual(len(res["mismatched_fields"]), 0)

    def test_mismatched_fields(self):
        p = {"full_name": "RAHUL SHARMA", "date_of_birth": "12/05/1992"}
        m = {"full_name": "RAHUL VERMA", "date_of_birth": "01/01/1990"}
        res = check_cross_document_consistency(p, mrz_fields=m)
        self.assertLess(res["consistency_score"], 80.0)
        self.assertTrue(len(res["mismatched_fields"]) >= 2)

if __name__ == "__main__":
    unittest.main()
