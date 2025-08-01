from src.security import hash_password, verify_password, authenticate_user


def test_password_hash():
    password = hash_password("Password1234")
    assert verify_password(password, "Password1234")


def test_authenticate(db):
    assert authenticate_user("Password@1234", "Dummy1")
