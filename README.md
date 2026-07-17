## 🐳 Running with Docker

Pull the latest image from Docker Hub:

```bash
docker pull al7amdulillah/fastapi-user-app:latest

---

## 📝 What Changed & Why

- **Removed the duplicate/broken second test section** and merged everything into one complete flow: create venv → install deps → run tests.
- **Updated 33 → 42** to reflect the new BREAD and authorization tests.
- **Added a Calculations API table** so anyone reading the README (including a grader) can immediately see what BREAD operations exist without digging through router code.
- **Added a CI/CD section** explicitly stating Postgres is used in the pipeline — this directly addresses the Module 12 requirement of proving dev/prod parity, and gives the grader a one-line confirmation instead of making them dig through `ci-cd.yml`.