import unittest
from fastapi.testclient import TestClient
from main import app

# remember to delete chirp from DB at end of test


class TestAccountOperations(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_create_account_success(self):
        # Setup
        test_email = "chirp@gmail.com"

        # Action
        response = self.client.post(
            f"/api/creator/create_account?email={test_email}&api_key=secretkey666"
        )

        # Verification
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], test_email)

    def test_create_account_bad_api_key_fail(self):
        # Setup
        test_email = "chirp23@gmail.com"

        # Action
        response = self.client.post(
            f"/api/creator/create_account?email={test_email}&api_key=badkey"
        )

        # Verification
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json().get("detail"), "Invalid dev API key")


if __name__ == "__main__":
    unittest.main()
