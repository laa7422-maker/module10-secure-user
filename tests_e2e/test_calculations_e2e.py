import uuid
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000"


def unique_email():
    return f"testuser_{uuid.uuid4().hex[:8]}@example.com"


def register_and_login(page: Page):
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
    return email, token


def goto_calculations(page: Page):
    page.goto(f"{BASE_URL}/static/calculations.html")
    page.wait_for_load_state("networkidle")
    print("DEBUG URL:", page.url)
    print("DEBUG TOKEN:", page.evaluate("() => localStorage.getItem('access_token')"))


def row_locator(page: Page, text: str):
    return page.locator("#calc-table-body tr", has_text=text)


# ---------------- Positive scenarios (full UI lifecycle) ----------------

def test_add_calculation_shows_in_table(page: Page):
    register_and_login(page)
    goto_calculations(page)

    page.fill("#a", "10")
    page.fill("#b", "5")
    page.select_option("#type", "Add")
    page.click("#submit-btn")

    expect(page.locator("#message")).to_contain_text("added", timeout=5000)
    row = row_locator(page, "15")
    expect(row).to_be_visible()
    expect(row).to_contain_text("10")
    expect(row).to_contain_text("Add")


def test_browse_shows_all_user_calculations(page: Page):
    register_and_login(page)
    goto_calculations(page)

    page.fill("#a", "2")
    page.fill("#b", "3")
    page.select_option("#type", "Multiply")
    page.click("#submit-btn")
    expect(page.locator("#message")).to_contain_text("added", timeout=5000)

    page.fill("#a", "20")
    page.fill("#b", "4")
    page.select_option("#type", "Sub")
    page.click("#submit-btn")
    expect(page.locator("#message")).to_contain_text("added", timeout=5000)

    expect(row_locator(page, "6")).to_be_visible()
    expect(row_locator(page, "16")).to_be_visible()


def test_edit_calculation_updates_row(page: Page):
    register_and_login(page)
    goto_calculations(page)

    page.fill("#a", "10")
    page.fill("#b", "5")
    page.select_option("#type", "Add")
    page.click("#submit-btn")
    expect(page.locator("#message")).to_contain_text("added", timeout=5000)

    row = row_locator(page, "15")
    row.get_by_role("button", name="Edit").click()

    page.fill("#b", "20")
    page.click("#submit-btn")

    expect(page.locator("#message")).to_contain_text("updated", timeout=5000)
    updated_row = row_locator(page, "30")
    expect(updated_row).to_be_visible()
    expect(updated_row).to_contain_text("20")

def test_delete_calculation_removes_row(page: Page):
    register_and_login(page)
    goto_calculations(page)

    page.fill("#a", "7")
    page.fill("#b", "3")
    page.select_option("#type", "Add")
    page.click("#submit-btn")
    expect(page.locator("#message")).to_contain_text("added", timeout=5000)

    page.on("dialog", lambda dialog: dialog.accept())   # 👈 ADD THIS LINE

    row = row_locator(page, "10")
    row.get_by_role("button", name="Delete").click()

    expect(page.locator("#message")).to_contain_text("deleted", timeout=5000)
    expect(page.locator("#calc-table-body")).not_to_contain_text("10")


# ---------------- Negative scenarios (direct API calls) ----------------

def get_auth_headers(page: Page):
    _, token = register_and_login(page)
    return {"Authorization": f"Bearer {token}"}


def test_create_with_divide_by_zero_returns_422(page: Page):
    headers = get_auth_headers(page)
    response = page.request.post(
        f"{BASE_URL}/calculations/",
        headers=headers,
        data={"a": 10, "b": 0, "type": "Divide"},
    )
    assert response.status == 422


def test_create_with_invalid_operation_returns_422(page: Page):
    headers = get_auth_headers(page)
    response = page.request.post(
        f"{BASE_URL}/calculations/",
        headers=headers,
        data={"a": 10, "b": 5, "type": "Modulo"},
    )
    assert response.status == 422


def test_browse_without_token_returns_401(page: Page):
    response = page.request.get(f"{BASE_URL}/calculations/")
    assert response.status == 401


def test_read_nonexistent_calculation_returns_404(page: Page):
    headers = get_auth_headers(page)
    response = page.request.get(f"{BASE_URL}/calculations/999999", headers=headers)
    assert response.status == 404


def test_delete_nonexistent_calculation_returns_404(page: Page):
    headers = get_auth_headers(page)
    response = page.request.delete(f"{BASE_URL}/calculations/999999", headers=headers)
    assert response.status == 404


def test_user_cannot_access_other_users_calculation(page: Page):
    headers_a = get_auth_headers(page)
    create_resp = page.request.post(
        f"{BASE_URL}/calculations/",
        headers=headers_a,
        data={"a": 1, "b": 2, "type": "Add"},
    )
    assert create_resp.status == 201
    calc_id = create_resp.json()["id"]

    headers_b = get_auth_headers(page)

    response = page.request.get(f"{BASE_URL}/calculations/{calc_id}", headers=headers_b)
    assert response.status == 404
