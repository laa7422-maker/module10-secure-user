import uuid
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000"


def unique_email():
    return f"testuser_{uuid.uuid4().hex[:8]}@example.com"


def test_register_with_valid_data_shows_success(page: Page):
    page.goto(f"{BASE_URL}/static/register.html")
    page.fill("#username", f"user_{uuid.uuid4().hex[:6]}")
    page.fill("#email", unique_email())
    page.fill("#password", "StrongPass123")
    page.fill("#confirm_password", "StrongPass123")
    page.click("button[type=submit]")

    expect(page.locator("#message")).to_contain_text("Registration successful", timeout=5000)


def test_register_with_short_password_shows_error(page: Page):
    page.goto(f"{BASE_URL}/static/register.html")
    page.fill("#username", "shortpassuser")
    page.fill("#email", unique_email())
    page.fill("#password", "123")
    page.fill("#confirm_password", "123")
    page.click("button[type=submit]")

    expect(page.locator("#message")).to_contain_text("at least 8 characters")


def test_register_with_mismatched_passwords_shows_error(page: Page):
    page.goto(f"{BASE_URL}/static/register.html")
    page.fill("#username", "mismatchuser")
    page.fill("#email", unique_email())
    page.fill("#password", "StrongPass123")
    page.fill("#confirm_password", "DifferentPass123")
    page.click("button[type=submit]")

    expect(page.locator("#message")).to_contain_text("do not match")


def test_login_with_valid_credentials_succeeds(page: Page):
    email = unique_email()
    password = "StrongPass123"

    page.goto(f"{BASE_URL}/static/register.html")
    page.fill("#username", f"user_{uuid.uuid4().hex[:6]}")
    page.fill("#email", email)
    page.fill("#password", password)
    page.fill("#confirm_password", password)
    page.click("button[type=submit]")
    expect(page.locator("#message")).to_contain_text("Registration successful", timeout=5000)

    page.goto(f"{BASE_URL}/static/login.html")
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type=submit]")

    expect(page.locator("#message")).to_contain_text("Login successful", timeout=5000)
    token = page.evaluate("() => localStorage.getItem('access_token')")
    assert token is not None and len(token) > 10


def test_login_with_wrong_password_shows_error(page: Page):
    email = unique_email()
    password = "StrongPass123"

    page.goto(f"{BASE_URL}/static/register.html")
    page.fill("#username", f"user_{uuid.uuid4().hex[:6]}")
    page.fill("#email", email)
    page.fill("#password", password)
    page.fill("#confirm_password", password)
    page.click("button[type=submit]")
    expect(page.locator("#message")).to_contain_text("Registration successful", timeout=5000)

    page.goto(f"{BASE_URL}/static/login.html")
    page.fill("#email", email)
    page.fill("#password", "WrongPassword999")
    page.click("button[type=submit]")

    expect(page.locator("#message")).to_contain_text("Incorrect email or password")
