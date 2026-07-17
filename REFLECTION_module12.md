# Reflection: Module 12 — User Endpoints, Calculation BREAD API & CI/CD

## What I Built

Building on the authentication foundation from Module 10, this module added
`POST /users/register` and `POST /users/login` endpoints using `UserCreate`
and secure password hashing, plus full BREAD (Browse, Read, Edit, Add,
Delete) operations on calculations, scoped to the authenticated user. The
implementation is validated by 42 automated integration tests running in
GitHub Actions, with a pipeline that builds, tests, and pushes a Docker
image to Docker Hub only when the full suite passes.

## Key Challenges Faced

**1. JWT `sub` Claim Mismatch Between Login and Auth Dependency**

The most subtle bug I encountered was a silent authentication failure. My
`/login` endpoint encoded the user's *username* into the JWT `sub` claim,
while `get_current_user` — the dependency protecting every calculation
route — decoded `sub` expecting a *numeric user ID* to look up the record.
Login itself returned 200 with a valid-looking token, so the failure only
surfaced one layer downstream, on the very next authenticated request
(`/me` and every calculation endpoint returned 401). The fix was
standardizing both `/login` and `/token` to encode `str(user.id)`
consistently, matching what the dependency expected on decode. This taught
me that a cryptographically valid JWT says nothing about whether its
payload's *meaning* matches what every consumer of that token expects —
correctness has to be verified end-to-end across every layer that touches
the token, not just at the point of issuance.

**2. Enforcing Per-User Ownership on Calculation Routes**

Implementing BREAD meant more than basic CRUD — every query had to be
scoped so that User A could never read, edit, or delete User B's
calculations, even by correctly guessing a valid ID. Rather than assuming
ownership checks were "obviously" correct once written, I wrote explicit
negative-path tests for this boundary
(`test_user_cannot_access_another_users_calculation`,
`test_unauthenticated_request_rejected`). This reinforced that authorization
belongs at the database query level — filtering by `user_id` directly in
the query itself — rather than as a check performed after fetching the
record, since the latter can leak information (like whether a given ID
exists at all) even while correctly denying access to it.

**3. Duplicate Authentication Logic Across Files**

During debugging, I discovered `get_current_user` and `oauth2_scheme` were
defined independently in both `main.py` and `dependencies.py`. They happened
to agree at the time, but this is exactly the kind of duplication that lets
two implementations quietly drift apart — a fix applied to one location can
be forgotten in the other. Consolidating auth logic into a single source of
truth in `dependencies.py` was a necessary follow-up once the `sub` claim
bug was fixed, to prevent the same class of bug from resurfacing.

**4. Confirming CI Actually Deploys, Not Just Builds Locally**

It was tempting to consider the Docker piece "done" once `docker build`
succeeded on my own machine. Verifying the pipeline required checking two
independent things: that GitHub Actions showed a green run on the Actions
tab, and that Docker Hub itself showed a freshly pushed image with a
matching timestamp. Only seeing both together confirmed the automated
pipeline — not a manual step on my laptop — was what actually produced the
deployed image.

## What I Learned

- A valid, decodable JWT does not guarantee semantic correctness — every
  consumer of a token's claims needs to agree on what those claims mean.
- Authorization checks are strongest when pushed down to the query level,
  not layered on top of an already-fetched record.
- Integration bugs often live in the *disagreement* between two components
  that are each individually correct in isolation — the `sub` claim bug is
  the clearest example: the login endpoint, the JWT library, and the auth
  dependency were each correct on their own terms, and the bug only existed
  in the gap between them.
- Local success (passing tests, a locally built Docker image) is not the
  same as verified success — CI logs and the Docker Hub registry itself are
  the actual source of truth for whether the pipeline works.

## What I'd Do Differently

I'd consolidate `get_current_user` into a single file from the very start of
the project, rather than letting duplicate definitions exist across two
files — that duplication is exactly what allowed the `sub` claim mismatch to
persist without being caught earlier by a simple code review. Given more
time, I'd also add rate limiting to the login endpoint to guard against
brute-force attempts, and implement refresh tokens to support longer-lived
sessions without weakening security guarantees.
