from argon2 import PasswordHasher
from .models import UserAccount

password_hasher = PasswordHasher()


def verify_password(hashed_password, plain_password):
    return password_hasher.verify(hashed_password, plain_password)


def hash_password(password):
    return password_hasher.hash(password)


def authenticate_user(password, email):
    UserAccount.get(UserAccount.email == email)
