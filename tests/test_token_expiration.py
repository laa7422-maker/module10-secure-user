from datetime import timedelta
from app.security import create_access_token


def test_me_with_expired_token(client, existing_user):
    # Log in normally first to confirm the user exists
    client.post("/login", json=existing_user)

    # Manually create a token that's already expired
    expired_token = create_access_token(
        data={"sub": existing_user["username"]},
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
