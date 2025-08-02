from argon2 import PasswordHasher

password_hasher = PasswordHasher()


def verify_password(hashed_password: str, plain_password: str) -> bool:
    return password_hasher.verify(hashed_password, plain_password)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)
