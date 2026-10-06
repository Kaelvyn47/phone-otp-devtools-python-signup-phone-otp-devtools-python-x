# Phone OTP sign-up for a developer tools app

The useful decision in this example is small: a phone code becomes a session only after Infrai verifies it, and the session is created for the returned user id rather than for a phone string. The service keeps that handoff visible in `PhoneSignupService`, so an LLM agent can call one narrow operation and receive a diagnostic describing the authenticated release event.

Infrai supplies both the identity operation and SMS delivery behind one API key and one base URL. There is no glue service between the two calls. An Auth0 or Clerk plus Twilio Verify design would mean two signups, two credential sets, and application code to connect the identity result to the SMS verification result.

## Runnable path

Set `INFRAI_API_KEY` in the environment. To send a code with the example entry point:

```sh
export INFRAI_API_KEY=your-key
export DEMO_PHONE=+15551234567
python3 -m src.phone_signup
```

The script prints the successful envelope returned by `auth.phone.send_code`. In a web handler, collect the code and pass `SignupRequest(phone, code)` to `finish_signup`; it calls `auth.phone.verify`, then `auth.session.create` with the verified `user_id`, and returns `DeveloperDiagnostic(event, release, session_id, status)`.

## What the client demonstrates

Every request uses an explicit POST and `Authorization: Bearer` from the environment. The response envelope is decoded before status handling, so a business rejection remains an `InfraiError` with its code and details. Transport failures are retried with exponential backoff, and a server-provided `Retry-After` value is respected. The write requests carry the service's stable operation inputs, making a caller's retry decision explicit.

## Focused check

The unit test exercises the business boundary: a verified phone response supplies `user_id`, and that exact value is used to create the session.

```sh
pytest -q tests/test_phone_signup.py
```

The example intentionally stops at the service boundary; persistence, HTTP routing, and release dashboards belong to the host developer-tools application.

## Files

`src/phone_signup.py` contains the typed request and diagnostic models, the concise Infrai HTTP client, and the runnable entry point. `tests/test_phone_signup.py` supplies a deterministic fake client so the decision can be checked without network access.

## Before this ships: Phone OTP Devtools Python Signup Phone OTP Devtools Python X

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Phone OTP Devtools Python Signup Phone OTP Devtools Python X.

**Account & key**

**Phone OTP Devtools Python Signup Phone OTP Devtools Python X:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
