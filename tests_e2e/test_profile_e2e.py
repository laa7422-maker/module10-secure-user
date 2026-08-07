import uuid
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000"


def unique_email():
    return f"testuser_{uuid.uuid4().hex[:8]}@example.com"


def register_and_login(page: Page, email: str, password: str):
    """Shared helper: register a fresh user and log in, leaving the
    browser authenticated with a valid access_token in localStorage."""
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


def test_profile_password_change_flow(page: Page):
    """Full positive flow: register -> login -> update profile ->
    change password -> logout -> re-login with the NEW password."""
    email = unique_email()
    old_password = "StrongPass123"
    new_password = "EvenStrongerPass456"

    register_and_login(page, email, old_password)

    page.goto(f"{BASE_URL}/static/profile.html")

    # Update profile info
    page.fill("#full-name", "Test User Updated")
    page.click("#update-profile-form button[type=submit]")
    expect(page.locator("#profile-message")).to_contain_text(
        "Profile updated successfully", timeout=5000
    )

    # Change password
    page.fill("#current-password", old_password)
    page.fill("#new-password", new_password)
    page.fill("#confirm-new-password", new_password)
    page.click("#password-form button[type=submit]")
    expect(page.locator("#password-message")).to_contain_text(
        "Password changed successfully", timeout=5000
    )

    # Logout
    page.click("#logout-btn")
    expect(page).to_have_url(f"{BASE_URL}/static/login.html")

    # Re-login with the NEW password proves the change persisted
    page.fill("#email", email)
    page.fill("#password", new_password)
    page.click("button[type=submit]")
    expect(page.locator("#message")).to_contain_text("Login successful", timeout=5000)


def test_password_change_with_wrong_current_password_shows_error(page: Page):
    """Negative flow: an incorrect current_password must be rejected
    with a clear error, and the old password must still work afterward."""
    email = unique_email()
    password = "StrongPass123"

    register_and_login(page, email, password)

    page.goto(f"{BASE_URL}/static/profile.html")

    page.fill("#current-password", "TotallyWrongPassword999")
    page.fill("#new-password", "NewPassword789")
    page.fill("#confirm-new-password", "NewPassword789")
    page.click("#password-form button[type=submit]")

    expect(page.locator("#password-message")).to_contain_text(
        "incorrect", timeout=5000
    )


def test_password_change_with_mismatched_confirmation_shows_error(page: Page):
    """Client-side guard: new password and confirmation must match
    before the request even reaches the backend."""
    email = unique_email()
    password = "StrongPass123"

    register_and_login(page, email, password)

    page.goto(f"{BASE_URL}/static/profile.html")

    page.fill("#current-password", password)
    page.fill("#new-password", "NewPassword789")
    page.fill("#confirm-new-password", "SomethingElseEntirely")
    page.click("#password-form button[type=submit]")

    expect(page.locator("#password-message")).to_contain_text("do not match")
