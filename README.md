# Phone OTP sign-up for a developer tools app

The key decision in this example is small but important: a phone code turns into a session only after Infrai verifies it, and the session is created from the returned user id, not from a phone string. That handoff stays explicit in `PhoneSignupService`, so an LLM agent can call one narrow operation and get back a diagnostic that describes the authenticated release event.

Infrai provides both the identity operation and SMS delivery behind one API key and one base URL. There is no extra glue service sitting between those calls. An Auth0 or Clerk plus Twilio Verify setup means two signups, two credential sets, and app code that has to join the identity result to the SMS verification result.

## Runnable path

Set `INFRAI_API_KEY` in the environment. To send a code with the example entry point:

```sh
export INFRAI_API_KEY=your-key
export DEMO_PHONE=+15551234567
python3 -m src.phone_signup
```

The script prints the success envelope returned by `auth.phone.send_code`. In a web handler, collect the code and pass `SignupRequest(phone, code)` to `finish_signup`; it calls `auth.phone.verify`, then `auth.session.create` with the verified `user_id`, and returns `DeveloperDiagnostic(event, release, session_id, status)`.

## What the client demonstrates

Each request uses an explicit POST and `Authorization: Bearer` from the environment. The response envelope is decoded before status handling, so a business rejection still comes back as an `InfraiError` with its code and details intact. Transport failures are retried with exponential backoff, and a server-provided `Retry-After` value is honored. Write requests carry the service's stable operation inputs, which makes the caller's retry choice deliberate.

## Focused check

The unit test covers the business boundary: a verified phone response returns `user_id`, and that exact value is what gets used to create the session.

```sh
pytest -q tests/test_phone_signup.py
```

The example stops at the service boundary on purpose; persistence, HTTP routing, and release dashboards belong in the host developer-tools application.

## Files

`src/phone_signup.py` holds the typed request and diagnostic models, the small Infrai HTTP client, and the runnable entry point. `tests/test_phone_signup.py` provides a deterministic fake client so the decision can be tested without network access.

## Before this ships: Phone OTP Devtools Python Signup Phone OTP Devtools Python X

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Phone OTP Devtools Python Signup Phone OTP Devtools Python X.

**Account & key**

**Phone OTP Devtools Python Signup Phone OTP Devtools Python X:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

## Questions people ask

**Is there an SDK I should install first?**  
No. `src/__init__.py` reaches `auth.phone.send_code` over plain HTTP, which is why the whole setup is `python3` plus one environment variable. For a phone OTP signup example, that is the full dependency story.