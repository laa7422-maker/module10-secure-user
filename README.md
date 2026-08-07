# FastAPI Secure Calculation API

![CI](https://github.com/laa7422-maker/module10-secure-user/actions/workflows/playwright.yml/badge.svg)

A FastAPI backend providing user registration, JWT-based authentication,
and full BREAD (Browse, Read, Edit, Add, Delete) operations on calculations,
scoped per authenticated user. Fully containerized and deployed via a
GitHub Actions CI/CD pipeline, with automated Playwright E2E tests gating
every Docker Hub release.

## 🔗 Links

- **GitHub Repository:** https://github.com/laa7422-maker/module10-secure-user
- **Docker Hub:** https://hub.docker.com/r/al7amdulillah/fastapi-user-app
- **Reflections:**
  - [Module 12](./REFLECTION_module12.md) — JWT sub claim fix, BREAD groundwork
  - [Module 13](./REFLECTION_module13.md) — Front-end integration, Docker deploy
  - [Module 14](./REFLECTION_module14.md) — Full BREAD implementation, CI/CD hardening

## 🧱 Tech Stack

- FastAPI
- PostgreSQL + SQLAlchemy (production) / SQLite (CI + quick local testing)
- Pydantic v2 (validation)
- JWT (python-jose) + bcrypt (passlib)
- Pytest (unit + integration testing)
- Playwright (end-to-end browser testing)
- Docker + GitHub Actions (CI/CD)

## 🔐 Security Features

This project applies secure authentication and authorization practices
throughout, satisfying CLO13:

- **Password hashing:** All user passwords are hashed with `bcrypt`
  (via `passlib`) before storage — plaintext passwords are never
  persisted to the database.
- **JWT-based sessions:** Login issues a signed JWT (`python-jose`,
  `HS256`), verified on every protected route via dependency injection.
- **Token expiration:** Access tokens expire after
  `ACCESS_TOKEN_EXPIRE_MINUTES` (default 30 minutes), enforced and
  covered by `tests/test_token_expiration.py`.
- **Per-user data scoping:** Every calculation is tied to the
  authenticated user's ID — users cannot browse, read, edit, or delete
  another user's records (enforced at the query level, verified by
  `test_user_cannot_access_other_users_calculation`).
- **Input validation:** All request bodies are validated through
  Pydantic v2 schemas, rejecting malformed or out-of-range input with
  `422 Unprocessable Entity` before it ever reaches business logic.
- **Self-service password changes:** Authenticated users can change
  their own password via `POST /users/me/password`, which requires
  re-verification of the *current* password (bcrypt comparison) before
  the new one is hashed and stored — preventing session-hijacking
  attacks from silently taking over an account.


## 👤 User Profile & Password Management

Authenticated users can view and update their own profile, and change
their password, through both the API and a dedicated front-end page.

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `PATCH` | `/users/me` | Update `full_name` on the current user's profile |
| `POST` | `/users/me/password` | Change the current user's password (requires current password verification) |

Both endpoints require a valid JWT in the `Authorization: Bearer <token>`
header, and both are covered by unit tests (`tests/test_security.py`),
integration tests (`tests/test_users.py`), and a full browser-level E2E
test (`tests_e2e/test_profile_e2e.py`).

### Try it in the browser

1. Register and log in via `/static/login.html`.
2. Navigate to `/static/profile.html`.
3. Update your full name and click **Save Profile** — confirms the
   `PATCH /users/me` flow.
4. Enter your current password and a new password, then click
   **Change Password** — confirms the `POST /users/me/password` flow.
5. Log out and log back in using the **new** password to verify the
   change persisted.

## 🚀 Running Locally

### 1. Clone the repo

    git clone https://github.com/laa7422-maker/module10-secure-user.git
    cd module10-secure-user

### 2. Set up environment variables
Create a `.env` file in the project root:

    DATABASE_URL=postgresql://user:password@localhost:5432/yourdb
    SECRET_KEY=your-secret-key-here
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30

> 💡 For quick local testing without Postgres, `DATABASE_URL` falls back to
> `sqlite:///./test.db` if not set.

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Run the server

    uvicorn app.main:app --reload

The API will be available at `http://localhost:8000`, with interactive
Swagger docs at `http://localhost:8000/docs`.

## 🧪 Running Unit & Integration Tests

This project uses `pytest` with a real PostgreSQL database for integration
testing.

    pytest -v

To see a coverage report:

    pytest --cov=app --cov-report=term-missing

Expected result: **42 passed, 0 failed**.

## 🎭 End-to-End Testing (Playwright)

In addition to unit/integration tests, this project includes a real
browser-driven E2E suite that exercises the running API through
Playwright, covering both authentication and the full calculations
BREAD flow.

### Run locally

    # 1. Install Playwright browsers (one-time setup)
    playwright install --with-deps chromium

    # 2. Start the server in one terminal
    uvicorn app.main:app --host 0.0.0.0 --port 8000

    # 3. Run the full E2E suite in another terminal
    pytest tests_e2e/test_auth_e2e.py tests_e2e/test_calculations_e2e.py tests_e2e/test_profile_e2e.py -v

Expected result: **18 passed** — covering registration, login, the
full Browse/Add/Edit/Delete calculation flow, profile updates and
password changes, plus authorization edge cases (invalid input, missing
token, cross-user access, nonexistent records, incorrect current
password, mismatched password confirmation).

### Run in CI

Every push triggers `.github/workflows/playwright.yml`, which:

1. Applies database migrations with `alembic upgrade head`.
2. Runs the full unit and integration suite (`pytest tests/ -v`) —
   this must pass before any E2E test is attempted, keeping fast
   failures fast.
3. Starts the FastAPI app in the background against a disposable SQLite
   database.
4. Health-checks the server (`curl`-polls `/docs` for up to 15 attempts)
   before running any tests — if the server fails to boot, the raw
   `uvicorn` log is printed directly to the Actions console for fast
   debugging.
5. Runs the full Playwright E2E suite (auth + calculations + profile)
   against the live server.
6. On merge to `main`, builds and pushes a fresh Docker image to
   Docker Hub — but only if every step above succeeds.

## 🖱️ Manual Testing via OpenAPI (Swagger UI)

You can manually exercise every endpoint without writing any code:

1. Start the server (`uvicorn app.main:app --reload`) and open
   `http://localhost:8000/docs` in your browser.
2. **Register a user** — expand `POST /users/register`, click **Try it out**,
   provide a username/email/password, and execute. Expect a `201 Created`.
3. **Log in** — expand `POST /login` (or `/token`), enter the same
   credentials, and execute. Copy the `access_token` from the response body.
4. **Authorize** — click the green **Authorize** button (top-right, padlock
   icon), paste the token, and click **Authorize**. This applies the token to
   every subsequent request made from the Swagger UI.
5. **Create a calculation** — expand `POST /calculations/`, click **Try it
   out**, provide an operation (`add`, `subtract`, `multiply`, `divide`) and
   two operands, and execute. Expect a `201 Created` with your `user_id`
   attached to the record.
6. **Browse / Read / Edit / Delete** — repeat the same pattern with
   `GET /calculations/`, `GET /calculations/{id}`, `PUT /calculations/{id}`,
   and `DELETE /calculations/{id}` to confirm the full BREAD cycle.
7. **Confirm ownership scoping** — log in as a second user and attempt to
   access the first user's calculation ID directly; expect a `404` or `403`,
   confirming users cannot access each other's data.

## 🐳 Docker

### Pull the pre-built image

    docker pull al7amdulillah/fastapi-user-app:latest
    docker run -p 8000:8000 --env-file .env al7amdulillah/fastapi-user-app:latest

### Or build it yourself

    docker build -t fastapi-user-app .
    docker run -p 8000:8000 --env-file .env fastapi-user-app

## ⚙️ CI/CD Pipeline

The pipeline is defined in `.github/workflows/playwright.yml` and runs on
every push. It's split into two sequential jobs:

| Job | Trigger | What it does |
|---|---|---|
| `e2e-tests` | Every push | Applies Alembic migrations (`alembic upgrade head`), runs the unit/integration suite (`pytest tests/ -v`) as a fast-fail gate, installs Playwright browsers, boots the FastAPI app against a disposable SQLite DB, health-checks it, then runs the full Playwright E2E suite (`tests_e2e/test_auth_e2e.py`, `tests_e2e/test_calculations_e2e.py`, `tests_e2e/test_profile_e2e.py`). |

This ensures no broken code is ever deployed as a production image — the Docker build never runs if *any* of the three gates (unit tests, integration tests, or E2E tests) fail.

### 🔐 Required GitHub Secrets

For the `build-and-push` job to work, configure these under
**Settings → Secrets and variables → Actions**:

| Secret | Purpose |
|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub account used to push the image |
| `DOCKERHUB_TOKEN` | Docker Hub access token (not your password) |

> **Note:** A legacy `ci-cd.yml` workflow (Postgres-based unit tests) was
> removed in favor of the unified `playwright.yml` pipeline above, to avoid
> duplicate/conflicting runs on every push.

## 🖥️ Front-End Pages

With the server running (`uvicorn app.main:app --reload`), open:

Register: http://localhost:8000/static/register.html
Login: http://localhost:8000/static/login.html
Calculations Dashboard: http://localhost:8000/static/calculations.html
Profile & Password Change: http://localhost:8000/static/profile.html

All pages perform client-side validation before submitting to the API. On successful login, the JWT is stored in localStorage under access_token, and the user is automatically redirected to the calculations dashboard. The profile page reuses this same stored token to authenticate `PATCH /users/me` and `POST /users/me/password` requests, and redirects back to the login page after a successful password change so the user can confirm the new credentials work.

## Screenshots

### CI/CD Pipeline — GitHub Actions (Successful Run)
![GitHub Actions Success](screenshots/git%20hub%20workflow%20module%2014.png)

### Docker Hub — Image Successfully Pushed
![Docker Hub Deployment](screenshots/docker%20hub%20screen%20shot%20module%2014.png)

### Front-End — Add Calculation
![Add Calculation](screenshots/C%20%26%20R%20in%20Bread.png)

### Front-End — Edit Calculation
![Edit Calculation](screenshots/test%20edit.png)

### Front-End — Delete Calculation
![Delete Calculation](screenshots/delete%20button.png)

### Local E2E Test Run — All Calculation Tests Passing (Including Browse)
![Local Test Run](screenshots/actions%20run.png)

### Front-End Login Flow
![Login Success](screenshots/log%20in%20successful%20module%2013.png)

### Front-End Registration Flow
![Registration UI](screenshots/test%20account%20module%2013.png)

### Front-End Registration Flow
![Registration UI](screenshots/test%20account%20module%2013.png)
