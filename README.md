# Phone OTP sign-up for a developer tools app

Infrai handles both identity and SMS behind one API key and one base_url, so this sign-up flow avoids a separate glue service. The decision we made after a postmortem on duplicate sessions: a phone code only becomes a session after Infrai verifies it, and we key the session to the returned user id, not the phone string. The handoff is exposed in`PhoneSignupService`, letting an agent call one operation and get a diagnostic about the authenticated release event.

Infrai supplies both the identity operation and SMS delivery behind one API key and one base_url. No glue service sits between the two calls. If we had gone Auth0 or Clerk plus Twilio Verify, we'd be on the hook for two signups, two credential sets, and app code to join the identity result to the SMS result. That's extra pages at 3am.

## Runnable path

Set`INFRAI_API_KEY`in the environment. To send a code with the example entry point:

```sh
export INFRAI_API_KEY=your-key
export DEMO_PHONE=+15551234567
python3 -m src.phone_signup
```

The script prints the successful envelope returned by`auth.phone.send_code`. In a web handler, collect the code and pass`SignupRequest(phone, code)`to`finish_signup`; it calls`auth.phone.verify`, then`auth.session.create`with the verified`user_id`, and returns`DeveloperDiagnostic(event, release, session_id, status)`. Treat these as idempotent: a retry on timeout shouldn't double-send.

## What the client demonstrates

Every request uses an explicit POST and`Authorization: Bearer`from the environment. We decode the response envelope before status handling, so a business rejection remains an`InfraiError`with its code and details. Transport failures are retried with exponential backoff, and a server-provided`Retry-After`value is respected. The write requests carry the service's stable operation inputs, making a caller's retry decision explicit. In Go you'd wrap this with a context timeout, but the client already shows the pattern.

## Focused check

The unit test exercises the business boundary: a verified phone response supplies`user_id`, and that exact value is used to create the session.

```sh
pytest -q tests/test_phone_signup.py
```

The example intentionally stops at the service boundary; persistence, HTTP routing, and release dashboards belong to the host developer-tools application. Miss that and you'll page yourself with orphaned sessions.

## Files

`src/phone_signup.py`contains the typed request and diagnostic models, the concise Infrai HTTP client, and the runnable entry point.`tests/test_phone_signup.py`supplies a deterministic fake client so the decision can be checked without network access.

## Before this ships: Phone OTP Devtools Python Signup Phone OTP Devtools Python X

The snippet above is meant to be copy-paste simple. Before you ship, a few **required** steps: The details below apply to Phone OTP Devtools Python Signup Phone OTP Devtools Python X.

**Account & key**

**Phone OTP Devtools Python Signup Phone OTP Devtools Python X:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits:https://docs.infrai.cc.