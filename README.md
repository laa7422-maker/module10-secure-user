## 🐳 Running with Docker

Pull the latest image from Docker Hub:

```bash
docker pull al7amdulillah/fastapi-user-app:latest
```

Run the container:

```bash
docker run -p 8000:8000 --env-file .env al7amdulillah/fastapi-user-app:latest
```

Once running, visit the interactive API docs at:

```
http://localhost:8000/docs
```
## 🧪 Running Tests Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the test suite with coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

This project maintains high test coverage across **33 tests**, covering
user registration, login, JWT token lifecycle, protected routes,
password security, and the Calculation model — including unit tests
for the factory pattern and schema validation, plus integration tests
verifying database persistence.


## 🔗 Docker Hub Repository

The image is automatically built and pushed via GitHub Actions on every push to `main`.

**View on Docker Hub:** https://hub.docker.com/r/al7amdulillah/fastapi-user-app

## 🧪 Running Tests Locally

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
