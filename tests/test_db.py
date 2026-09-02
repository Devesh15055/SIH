"""Unit tests for SQLite Database Manager"""
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import init_db, save_screening_case, get_all_screening_cases, get_case_by_id

class TestDBManager(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_save_and_retrieve_case(self):
        case_id = "SIH2-DBTEST123"
        saved = save_screening_case(
            case_id=case_id,
            risk_score=22.5,
            classification="LOW RISK",
            decision="APPROVED",
            summary_data={"ocr_result": {"confidence": 90.0}}
        )
        self.assertTrue(saved)

        retrieved = get_case_by_id(case_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["case_id"], case_id)
        self.assertEqual(retrieved["final_risk_score"], 22.5)

        all_cases = get_all_screening_cases()
        self.assertTrue(len(all_cases) > 0)

if __name__ == "__main__":
    unittest.main()
