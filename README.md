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
- **Reflection:** [REFLECTION_module12.md](./REFLECTION_module12.md)

## 🧱 Tech Stack

- FastAPI
- PostgreSQL + SQLAlchemy (production) / SQLite (CI + quick local testing)
- Pydantic v2 (validation)
- JWT (python-jose) + bcrypt (passlib)
- Pytest (unit + integration testing)
- Playwright (end-to-end browser testing)
- Docker + GitHub Actions (CI/CD)

## 🚀 Running Locally

### 1. Clone the repo
```bash
git clone https://github.com/laa7422-maker/module10-secure-user.git
cd module10-secure-user
```

### 2. Set up environment variables
Create a `.env` file in the project root:
```
DATABASE_URL=postgresql://user:password@localhost:5432/yourdb
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> 💡 For quick local testing without Postgres, `DATABASE_URL` falls back to
> `sqlite:///./test.db` if not set.

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive
Swagger docs at `http://localhost:8000/docs`.

## 🧪 Running Unit & Integration Tests

This project uses `pytest` with a real PostgreSQL database for integration
testing.

```bash
pytest -v
```

To see a coverage report:
```bash
pytest --cov=app --cov-report=term-missing
```

Expected result: **42 passed, 0 failed**.

## 🎭 End-to-End Testing (Playwright)

In addition to unit/integration tests, this project includes a real
browser-driven E2E suite that exercises the running API through
Playwright.

### Run locally

```bash
# 1. Install Playwright browsers (one-time setup)
playwright install --with-deps chromium

# 2. Start the server in one terminal
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. Run the E2E suite in another terminal
pytest tests_e2e/test_auth_e2e.py -v
```

### Run in CI

Every push triggers `.github/workflows/playwright.yml`, which:

1. Starts the FastAPI app in the background against a disposable SQLite
   database.
2. Health-checks the server (`curl`-polls `/docs` for up to 15 attempts)
   before running any tests — if the server fails to boot, the raw
   `uvicorn` log is printed directly to the Actions console for fast
   debugging.
3. Runs the full Playwright E2E suite against the live server.

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
```bash
docker pull al7amdulillah/fastapi-user-app:latest
docker run -p 8000:8000 --env-file .env al7amdulillah/fastapi-user-app:latest
```

### Or build it yourself
```bash
docker build -t fastapi-user-app .
docker run -p 8000:8000 --env-file .env fastapi-user-app
```

## ⚙️ CI/CD Pipeline

The pipeline is defined in `.github/workflows/playwright.yml` and runs on
every push. It's split into two sequential jobs:

| Job | Trigger | What it does |
|---|---|---|
| **`e2e-tests`** | Every push | Installs dependencies + Playwright browsers, boots the FastAPI app with required env vars against a disposable SQLite DB, health-checks it, then runs the Playwright E2E suite (`tests_e2e/test_auth_e2e.py`). |
| **`build-and-push`** | Only on `main`, only if `e2e-tests` passes | Logs into Docker Hub and builds/pushes the image as `al7amdulillah/fastapi-user-app:latest`. |

This ensures no broken code is ever deployed as a production image — the
Docker build simply never runs if the E2E suite fails.

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

- **Register:** http://localhost:8000/static/register.html
- **Login:** http://localhost:8000/static/login.html

Both pages perform client-side validation before submitting to the API.
On successful login, the JWT is stored in `localStorage` under `access_token`.
## Screenshots

### CI/CD Pipeline — GitHub Actions
![GitHub Actions Success](github%20module%2013.png)

### Playwright E2E Tests — All Passing
![5 Passed Tests](5%20passed%20tests.png)

### Front-End Login Flow — JWT + /me Verification
![Front-end UI](screenshots-frontend-ui.png)
