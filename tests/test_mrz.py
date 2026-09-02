import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_modules.mrz_validation import validate_mrz, calculate_checksum

class TestMRZ(unittest.TestCase):
    def test_checksum_calculation(self):
        cs = calculate_checksum("L898902C3")
        self.assertTrue(0 <= cs <= 9)

    def test_passport_mrz_parsing(self):
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C36UTO7405192F1204159ZE184226B<<<<<10"
        res = validate_mrz([line1, line2])
        self.assertTrue(res["mrz_detected"])
        self.assertEqual(res["format"], "TD3 (Passport)")
        self.assertEqual(res["parsed_fields"]["surname"], "ERIKSSON")
        self.assertEqual(res["parsed_fields"]["given_names"], "ANNA MARIA")

    def test_non_mrz_fallback(self):
        res = validate_mrz(["NO MRZ HERE", "JUST RANDOM TEXT"])
        self.assertFalse(res["mrz_detected"])
        self.assertEqual(res["status_message"], "MRZ not present or not detected")

if __name__ == "__main__":
    unittest.main()
