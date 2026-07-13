# Reflection: Module 10 — Secure User Authentication & CI/CD

## What I Built

A FastAPI authentication system with bcrypt password hashing, JWT-based
session management, and protected routes, backed by 18 automated tests
achieving 95% coverage. The application is containerized with Docker and
deployed via a GitHub Actions CI/CD pipeline to Docker Hub.

## Key Challenges Faced

**1. Secret Key Shadowing**

Early in development, the application's `SECRET_KEY` was being silently
overridden instead of correctly loading from environment variables. This
taught me to be much more careful about environment variable precedence
and to always verify configuration is actually being loaded as intended,
not just assumed.

**2. Empty Dockerfile from a Platform Command Mismatch**

A Windows-specific command (`type nul > Dockerfile`) accidentally wiped
the Dockerfile's contents while I intended to just create the file. This
was a good reminder that shell commands behave differently across
operating systems, and it's worth double-checking file contents after
running unfamiliar commands.

**3. Missing GitHub Actions Workflow**

My CI/CD pipeline appeared to not exist in the Actions tab, even though
the workflow file existed locally. The root cause was that the
`.github/workflows/` directory had never actually been committed and
pushed to GitHub. This clarified an important lesson: local file
existence means nothing until it's actually tracked by git and pushed.

**4. Docker Hub Authentication Failures**

My first CI/CD run failed at the deploy stage with a
"Username and password required" error. This came down to GitHub
repository secrets not being correctly configured. I learned that Docker
Hub access tokens can only be viewed once at creation time, which means
losing one requires generating a completely new token rather than
retrieving the old value.

## What I Learned

- The difference between code working locally versus working in an
  automated, reproducible CI environment
- How environment variables and secrets flow differently across local
  development, Docker containers, and GitHub Actions
- The importance of verifying each stage of a pipeline independently
  (a passing test stage does not guarantee the deploy stage will pass)
- How to debug CI/CD failures using workflow run logs and annotations

## What I'd Do Differently

Given more time, I would add rate limiting to the login endpoint to
protect against brute-force attacks, and implement refresh tokens to
support longer-lived sessions without compromising security.
