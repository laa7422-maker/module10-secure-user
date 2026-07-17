# FastAPI Secure Calculation API

A FastAPI backend providing user registration, JWT-based authentication,
and full BREAD (Browse, Read, Edit, Add, Delete) operations on calculations,
scoped per authenticated user. Fully containerized and deployed via a
GitHub Actions CI/CD pipeline to Docker Hub.

## 🔗 Links

- **GitHub Repository:** https://github.com/laa7422-maker/module10-secure-user
- **Docker Hub:** https://hub.docker.com/r/al7amdulillah/fastapi-user-app
- **Reflection:** [REFLECTION_module12.md](./REFLECTION_module12.md)

## 🧱 Tech Stack

- FastAPI
- PostgreSQL + SQLAlchemy
- Pydantic v2 (validation)
- JWT (python-jose) + bcrypt (passlib)
- Pytest (integration testing)
- Docker + GitHub Actions (CI/CD)

## 🚀 Running Locally

### 1. Clone the repo
\`\`\`bash
git clone https://github.com/laa7422-maker/module10-secure-user.git
cd module10-secure-user
\`\`\`

### 2. Set up environment variables
Create a `.env` file in the project root:
\`\`\`
DATABASE_URL=postgresql://user:password@localhost:5432/yourdb
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
\`\`\`

### 3. Install dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Run the server
\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

The API will be available at `http://localhost:8000`, with interactive
Swagger docs at `http://localhost:8000/docs`.

## 🧪 Running Tests Locally

This project uses `pytest` with a real PostgreSQL database for integration
testing.

\`\`\`bash
pytest -v
\`\`\`

To see a coverage report:
\`\`\`bash
pytest --cov=app --cov-report=term-missing
\`\`\`

Expected result: **42 passed, 0 failed**.

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
\`\`\`bash
docker pull al7amdulillah/fastapi-user-app:latest
docker run -p 8000:8000 --env-file .env al7amdulillah/fastapi-user-app:latest
\`\`\`

### Or build it yourself
\`\`\`bash
docker build -t fastapi-user-app .
docker run -p 8000:8000 --env-file .env fastapi-user-app
\`\`\`

## ⚙️ CI/CD Pipeline

Every push to `main` triggers a GitHub Actions workflow that:

1. Spins up a PostgreSQL service container.
2. Installs dependencies and runs the full `pytest` suite (42 tests).
3. If — and only if — all tests pass, builds a Docker image and pushes it
   to Docker Hub tagged `latest`.

This ensures no broken code is ever deployed as a production image.
