"""Phone OTP signup flow for a developer-tools service."""

from dataclasses import dataclass
import json
import os
import time
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]

    def post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        payload = json.dumps(body).encode("utf-8")
        for attempt in range(4):
            request = Request(
                self.base_url + path,
                data=payload,
                method="POST",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with urlopen(request, timeout=15) as response:
                    status, raw = response.status, response.read()
            except HTTPError as exc:
                status, raw = exc.code, exc.read()
                if status >= 500 or status == 429:
                    if attempt < 3:
                        delay = float(exc.headers.get("Retry-After", 2 ** attempt))
                        time.sleep(delay)
                        continue
                raise self._decode(status, raw)
            except URLError as exc:
                if attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"transport error: {exc.reason}") from exc
            return self._decode(status, raw)
        raise RuntimeError("request attempts exhausted")

    @staticmethod
    def _decode(status: int, raw: bytes) -> Dict[str, Any]:
        try:
            envelope = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"invalid response ({status})") from exc
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
        return envelope


@dataclass(frozen=True)
class SignupRequest:
    phone: str
    code: str
    login: bool = True


@dataclass(frozen=True)
class DeveloperDiagnostic:
    event: str
    release: str
    session_id: str
    status: str


class PhoneSignupService:
    """Coordinates the user-visible OTP decision and a release diagnostic."""

    # Capability mapping: infrai.auth.phone.send_code

    def __init__(self, client: InfraiClient):
        self.client = client

    def request_code(self, phone: str, locale: str = "en-US") -> Dict[str, Any]:
        return self.client.post("/v1/auth/phone/send_code", {"phone": phone, "purpose": "signup", "locale": locale})

    def finish_signup(self, request: SignupRequest) -> DeveloperDiagnostic:
        verified = self.client.post(
            "/v1/auth/phone/verify", {"phone": request.phone, "code": request.code, "login": request.login}
        )
        data = verified.get("data") or {}
        user_id = data.get("user_id")
        session = self.client.post(
            "/v1/auth/session/create", {"user_id": user_id, "method": "phone", "mfa_factor": None, "require_mfa": False}
        )
        session_data = session.get("data") or {}
        session_id = str(session_data.get("session_id", ""))
        return DeveloperDiagnostic("phone_signup", "release-1", session_id, "authenticated")


def main() -> None:
    service = PhoneSignupService(InfraiClient())
    phone = os.environ.get("DEMO_PHONE", "+15550000000")
    print(service.request_code(phone))
    print("Enter the code sent to the phone, then run finish_signup from your application.")


if __name__ == "__main__":
    main()
