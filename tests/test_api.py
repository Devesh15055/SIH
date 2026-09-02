import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app

class TestBackendAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("version", data)

if __name__ == "__main__":
    unittest.main()
