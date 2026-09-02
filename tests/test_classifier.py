"""Unit tests for Document Type Classifier Engine"""
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_modules.ocr import classify_document

class TestDocumentClassifier(unittest.TestCase):
    def test_passport_classification(self):
        text = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<\nPASSPORT REPUBLIC OF INDIA"
        res = classify_document(text, mrz_detected=True)
        self.assertEqual(res["document_type"], "PASSPORT")
        self.assertEqual(res["document_label"], "Passport (ICAO 9303)")
        self.assertGreaterEqual(res["confidence"], 90.0)

    def test_aadhaar_classification(self):
        text = "GOVERNMENT OF INDIA\nUNIQUE IDENTIFICATION AUTHORITY OF INDIA\n1234 5678 9012"
        res = classify_document(text)
        self.assertEqual(res["document_type"], "AADHAAR")
        self.assertEqual(res["document_label"], "Aadhaar Card (UIDAI)")

    def test_pan_classification(self):
        text = "INCOME TAX DEPARTMENT\nPERMANENT ACCOUNT NUMBER\nABCDE1234F"
        res = classify_document(text)
        self.assertEqual(res["document_type"], "PAN_CARD")

    def test_generic_classification(self):
        text = "SOME UNKNOWN SAMPLE DOCUMENT TEXT"
        res = classify_document(text)
        self.assertEqual(res["document_type"], "GENERIC_ID")

if __name__ == "__main__":
    unittest.main()
