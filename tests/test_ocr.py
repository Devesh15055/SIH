import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_modules.ocr import extract_fields_from_text, extract_document_text

class TestOCR(unittest.TestCase):
    def test_indian_aadhaar_ocr_parsing(self):
        sample_text = """
        GOVERNMENT OF INDIA
        Name: Rahul Sharma
        DOB: 12/05/1992
        GENDER: MALE
        NATIONALITY: INDIAN
        1234 5678 9012
        """
        fields, warnings = extract_fields_from_text(sample_text)
        self.assertEqual(fields["full_name"], "Rahul Sharma")
        self.assertEqual(fields["date_of_birth"], "12/05/1992")
        self.assertEqual(fields["gender"], "Male")
        self.assertEqual(fields["document_number"], "1234 5678 9012")

    def test_ocr_missing_fields_warning(self):
        sample_text = "RANDOM BLURRY UNREADABLE TEXT"
        res = extract_document_text(sample_text)
        self.assertTrue(len(res["warnings"]) > 0)

if __name__ == "__main__":
    unittest.main()
