import sys, os
import unittest
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_modules.deepfake_detection import detect_deepfake_artifacts

class TestDeepfakeDetection(unittest.TestCase):
    def test_deepfake_artifacts_detection(self):
        blank = np.ones((200, 200, 3), dtype=np.uint8) * 120
        res = detect_deepfake_artifacts(blank)
        self.assertIn("screening_label", res)
        self.assertEqual(res["screening_label"], "Prototype AI-assisted screening")
        self.assertIn("disclaimer", res)
        self.assertIn("Prototype AI-assisted screening", res["disclaimer"])
        self.assertIn("quality_metrics", res)

if __name__ == "__main__":
    unittest.main()
