def test_login_json_success(client, existing_user):
    response = client.post(
        "/login",
        json={
            "username": existing_user["username"],
            "password": existing_user["password"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_json_wrong_password(client, existing_user):
    response = client.post(
        "/login",
        json={
            "username": existing_user["username"],
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


def test_login_json_nonexistent_user(client):
    response = client.post(
        "/login",
        json={"username": "ghostuser", "password": "whatever123"},
    )

    assert response.status_code == 401
def test_me_with_valid_token(client, existing_user):
    login_response = client.post(
        "/login",
        json={
            "username": existing_user["username"],
            "password": existing_user["password"],
        },
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == existing_user["username"]


def test_me_without_token(client):
    response = client.get("/me")
    assert response.status_code == 401


def test_me_with_invalid_token(client):
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer this.is.not.a.valid.token"},
    )
    assert response.status_code == 401
def test_token_form_success(client, existing_user):
    response = client.post(
        "/token",
        data={
            "username": existing_user["username"],
            "password": existing_user["password"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_token_form_wrong_password(client, existing_user):
    response = client.post(
        "/token",
        data={
            "username": existing_user["username"],
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


def test_token_form_nonexistent_user(client):
    response = client.post(
        "/token",
        data={"username": "ghostuser", "password": "whatever123"},
    )

    assert response.status_code == 401
def test_me_with_valid_token(client, existing_user):
    login_response = client.post(
        "/login",
        json={
            "username": existing_user["username"],
            "password": existing_user["password"],
        },
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == existing_user["username"]


def test_me_without_token(client):
    response = client.get("/me")
    assert response.status_code == 401


def test_me_with_invalid_token(client):
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer this.is.not.a.valid.token"},
    )
    assert response.status_code == 401
