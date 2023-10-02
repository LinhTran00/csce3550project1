import unittest
import json
from main import app  # Import your Flask app

class TestApp(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()

    def test_get_jwks(self):
        response = self.app.get('/.well-known/jwks.json')
        self.assertEqual(response.status_code, 200)
        jwks_data = json.loads(response.get_data(as_text=True))
        self.assertIn("keys", jwks_data)
        self.assertEqual(len(jwks_data["keys"]), 1)  # Check if there is only one key (the current key)

    def test_authenticate(self):
        response = self.app.post('/auth')
        self.assertEqual(response.status_code, 200)
        token = response.get_data(as_text=True)
        # You can add more assertions to validate the JWT token if needed

    def test_authenticate_expired(self):
        response = self.app.post('/auth?expired=true')
        self.assertEqual(response.status_code, 200)
        token = response.get_data(as_text=True)
        # You can add more assertions to validate the JWT token if needed

if __name__ == '__main__':
    unittest.main()
