def test_create_user_success(client):
    response = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpassword123",
        },
    )
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


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

    client.post("/users", json=payload_1)
    response = client.post("/users", json=payload_2)

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

    client.post("/users", json=payload_1)
    response = client.post("/users", json=payload_2)

    assert response.status_code == 400


def test_password_is_hashed_in_database(client):
    response = client.post(
        "/users",
        json={
            "username": "secureuser",
            "email": "secure@example.com",
            "password": "plaintextpassword",
        },
    )
    assert response.status_code == 201
    assert "plaintextpassword" not in response.text
