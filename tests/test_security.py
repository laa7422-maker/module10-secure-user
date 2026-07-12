from app.security import hash_password, verify_password


def test_hash_password_produces_different_hash_than_input():
    plain = "mypassword123"
    hashed = hash_password(plain)

    assert hashed != plain
    assert len(hashed) > 0


def test_verify_password_success():
    plain = "mypassword123"
    hashed = hash_password(plain)

    assert verify_password(plain, hashed) is True


def test_verify_password_failure():
    plain = "mypassword123"
    hashed = hash_password(plain)

    assert verify_password("wrongpassword", hashed) is False


def test_hash_password_is_salted():
    # Hashing the same password twice should NOT produce identical hashes.
    # If it does, you're missing a salt — a serious security flaw.
    plain = "mypassword123"
    hash_one = hash_password(plain)
    hash_two = hash_password(plain)

    assert hash_one != hash_two
