# Module 13 Reflection

## Building JWT Auth + Front-End Forms
- Wiring `register.js`/`login.js` to hit FastAPI JSON endpoints instead of
  form-encoded submissions.
- Deciding what validation belongs client-side (fast feedback) vs.
  server-side (source of truth) — e.g. password length checked in both places.

## The CI/CD Debugging Challenge
- Playwright E2E tests failed in GitHub Actions with `ERR_CONNECTION_REFUSED`,
  even though everything worked locally.
- Root cause: the FastAPI server needs `SECRET_KEY` and `DATABASE_URL` to boot,
  but GitHub Actions runners don't inherit local `.env` files — the server was
  silently crashing before Playwright could ever connect.
- Fix: explicitly injected env vars into the workflow step, and added log
  capture (`> server.log 2>&1`) so failed health checks print the real
  traceback instead of failing silently.
- Lesson: **CI environments are not your laptop.** Anything implicit
  locally (env vars, `.env` files, default ports) must be made explicit
  in the workflow.

## Key Takeaway
Automated testing is only as trustworthy as the environment it runs in —
a passing local test means little if the CI server can't even start.
