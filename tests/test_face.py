import sys, os
import unittest
import numpy as np
import cv2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_modules.face_verification import verify_faces, detect_faces, check_image_quality, compute_face_similarity

class TestFaceVerification(unittest.TestCase):
    def test_face_quality_checker(self):
        blank = np.ones((200, 200, 3), dtype=np.uint8) * 128
        metrics, warnings = check_image_quality(blank)
        self.assertEqual(metrics["width"], 200)
        self.assertEqual(metrics["height"], 200)
        self.assertIn("sharpness_score", metrics)

    def test_similarity_same_image(self):
        chip = np.zeros((128, 128, 3), dtype=np.uint8)
        cv2.circle(chip, (64, 64), 30, (200, 180, 150), -1)
        sim = compute_face_similarity(chip, chip)
        self.assertGreaterEqual(sim, 90.0)

    def test_verify_faces_missing_selfie(self):
        blank = np.ones((200, 200, 3), dtype=np.uint8) * 128
        res = verify_faces(blank, selfie_img_input=None)
        self.assertEqual(res["status"], "INCONCLUSIVE")
        self.assertFalse(res["selfie_face_detected"])
        self.assertIn("No selfie photo provided for facial matching.", res["quality_warnings"])

if __name__ == "__main__":
    unittest.main()
