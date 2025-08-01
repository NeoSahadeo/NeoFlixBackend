from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from peewee import DoesNotExist
from .models import UserAccount

password_hasher = PasswordHasher()


def verify_password(hashed_password: str, plain_password: str) -> bool:
    return password_hasher.verify(hashed_password, plain_password)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def authenticate_user(password: str, username: str) -> UserAccount | bool:
    try:
        user: UserAccount = UserAccount.get(UserAccount.username == username)
        if user and verify_password(user.hashed_password, password):
            return user
    except VerifyMismatchError or DoesNotExist:
        pass
    return False
