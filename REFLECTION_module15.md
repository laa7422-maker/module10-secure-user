# Module 15 Reflection: User Profile & Password Management

## Overview

This module extended the FastAPI Calculations application with a
self-service **User Profile & Password Change** feature, along with a
hardened CI/CD pipeline that gates deployment behind a full,
multi-layer automated test suite. The goal was not just to add a new
feature, but to prove — through automated tests at every layer — that
it works correctly *and* securely before it ever reaches production.

## What Was Built

- **Backend:** Two new authenticated endpoints on `app/routers/users.py`
  — `PATCH /users/me` for updating profile fields (full name), and
  `POST /users/me/password` for changing a password.
- **Frontend:** A new `static/profile.html` page with accompanying
  `static/js/profile.js`, mirroring the existing login/register UI
  patterns so the JWT-based auth flow stayed consistent across the app.
- **Testing:** Unit and integration coverage in `tests/test_users.py`,
  plus a full browser-driven end-to-end test
  (`tests_e2e/test_profile_e2e.py`) that walks through the entire real
  user journey: log in, update profile, change password, log out, and
  log back in with the *new* password to confirm the change actually
  persisted.
- **CI/CD:** Updated `.github/workflows/playwright.yml` so the pipeline
  now runs Alembic migrations, then the unit/integration suite, then
  the full Playwright E2E suite — and only pushes a new Docker image to
  Docker Hub if *all three* gates pass.

## Security Significance

The most important design decision in this feature was requiring users
to re-enter their **current password** before a new one is accepted.
This might look like a small detail, but it closes a real vulnerability
class: without it, anyone who managed to steal or reuse an active
session token (through XSS, a shared device, or a leaked JWT) could
silently change the account's password and lock the real owner out
permanently. Requiring current-password verification means a hijacked
*session* is not enough on its own to hijack the *account* — the
attacker would also need to know the actual password, which defeats
the purpose of stealing a session token in the first place.

On the implementation side, passwords are never compared or stored in
plaintext. The current password is checked using `passlib`'s `bcrypt`
verification against the stored hash, and the new password is re-hashed
with a fresh bcrypt salt before being written to the database. This
matches the same hashing approach already used at registration, so
there's no weaker "backdoor" path for setting a password outside the
normal secure flow.

Testing this properly meant covering the failure paths just as
carefully as the success path: wrong current password rejected,
missing auth token rejected, and the edge case of submitting the exact
same password as the current one (which should succeed, since it's not
a security risk, just a no-op-style update).

## Challenges Resolved

The trickiest part of this module wasn't the feature code itself — it
was a Git workflow mistake that turned into a genuinely useful lesson.
After finishing the README documentation updates, I ran `git commit`
and `git push origin main`, but the push was rejected with a
`fast-forward` error. Tracing through the terminal output, the root
cause became clear: the commit had landed on my old
`feature/profile-ui-and-e2e` branch, not `main`, because I hadn't
switched branches after the PR had already been merged on GitHub. Local
`main` was also out of date relative to the remote, which compounded
the confusion.

The fix required three steps in sequence: checking out `main`, pulling
the latest remote state to catch it up to the already-merged PR, and
then merging the feature branch into it locally to bring the README
commit across without losing any history. Git opened a Vim editor to
confirm the merge commit message, which was an unfamiliar interface at
first, but resolved cleanly once I saved and exited with `:wq`. After
that, the push succeeded, and the feature branch could be safely
deleted both locally and on GitHub, since its work was now fully
captured in `main`'s history.

This reinforced a habit I'll carry forward: always confirm which
branch you're on with `git status` or `git branch` *before* committing,
especially right after a PR merge — it's an easy assumption to get
wrong, and the fix is simple once you understand what Git is actually
telling you.

## Alignment with Course Learning Outcomes

- **CLO3 (Automated Testing):** New unit, integration, and E2E tests
  were written specifically for the profile/password feature, bringing
  the full suite to 18 passing E2E tests plus the underlying
  unit/integration layer.
- **CLO4 (CI Automation):** The pipeline now enforces a strict
  migrations → unit/integration → E2E gate sequence, with Docker builds
  blocked entirely if any stage fails.
- **CLO10 (REST APIs):** The new endpoints follow the same RESTful
  conventions (proper HTTP methods, status codes, and JWT-based auth)
  as the rest of the application.
- **CLO13 (Secure Authentication):** The password-change flow
  specifically defends against session-hijacking account takeovers by
  requiring current-password re-verification, and all password
  handling relies on bcrypt hashing rather than plaintext comparison
  or storage.

## Final Thoughts

This module tied together everything from earlier in the course —
schema migrations, secure auth, layered testing, and CI/CD — into one
cohesive feature addition. The Git mishap was a reminder that shipping
software isn't just about writing correct code; it's also about
understanding the tools and workflows around that code well enough to
recover quickly when something unexpected happens.
