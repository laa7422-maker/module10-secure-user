def test_create_user_success(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpassword123",
        },
    )
    assert response.status_code == 201


def test_duplicate_username_rejected(client):
    payload_1 = {
        "username": "dupeuser",
        "email": "first@example.com",
        "password": "password123",
    }
    payload_2 = {
        "username": "dupeuser",
        "email": "second@example.com",
        "password": "password123",
    }

    client.post("/users/register", json=payload_1)
    response = client.post("/users/register", json=payload_2)

    assert response.status_code == 400


def test_duplicate_email_rejected(client):
    payload_1 = {
        "username": "user_one",
        "email": "same@example.com",
        "password": "password123",
    }
    payload_2 = {
        "username": "user_two",
        "email": "same@example.com",
        "password": "password123",
    }

    client.post("/users/register", json=payload_1)
    response = client.post("/users/register", json=payload_2)

    assert response.status_code == 400

def test_password_is_hashed_in_database(client):
    response = client.post(
        "/users/register",
        json={
            "username": "secureuser",
            "email": "secure@example.com",
            "password": "plaintextpassword",
        },
    )
    assert response.status_code == 201
    assert "plaintextpassword" not in response.text

def test_update_full_name_success(client, auth_headers):
    response = client.patch(
        "/users/me",
        json={"full_name": "Auth User Updated"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == "Auth User Updated"


def test_update_profile_requires_auth(client):
    response = client.patch("/users/me", json={"full_name": "No Auth"})
    assert response.status_code == 401


def test_change_password_success(client, auth_headers):
    response = client.post(
        "/users/me/password",
        json={
            "current_password": "securepassword123",
            "new_password": "newsecurepassword456",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200

    login_response = client.post(
        "/users/login",
        json={"email": "authuser@example.com", "password": "newsecurepassword456"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_change_password_wrong_current_password(client, auth_headers):
    response = client.post(
        "/users/me/password",
        json={
            "current_password": "totallywrongpassword",
            "new_password": "newsecurepassword456",
        },
        headers=auth_headers,
    )
    assert response.status_code == 401


def test_change_password_same_as_current(client, auth_headers):
    response = client.post(
        "/users/me/password",
        json={
            "current_password": "securepassword123",
            "new_password": "securepassword123",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422
