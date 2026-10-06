import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.phone_signup import InfraiClient, PhoneSignupService, SignupRequest


class FakeClient(InfraiClient):
    def __init__(self):
        self.calls = []

    def post(self, path, body):
        self.calls.append((path, body))
        if path.endswith("send_code"):
            return {"ok": True, "data": {"sent": True}, "error": None, "metadata": {}}
        if path.endswith("verify"):
            return {"ok": True, "data": {"user_id": "user_42"}, "error": None, "metadata": {}}
        return {"ok": True, "data": {"session_id": "sess_42"}, "error": None, "metadata": {}}


class SignupDecisionTest(unittest.TestCase):
    def test_verified_phone_creates_session_for_same_user(self):
        client = FakeClient()
        service = PhoneSignupService(client)
        result = service.finish_signup(SignupRequest("+15551234567", "123456"))
        self.assertEqual(result.status, "authenticated")
        self.assertEqual(client.calls[1][1]["user_id"], "user_42")
        self.assertEqual(client.calls[1][1]["method"], "phone")


if __name__ == "__main__":
    unittest.main()
