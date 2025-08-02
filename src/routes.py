from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel

import jwt
from jwt.exceptions import InvalidTokenError

from argon2.exceptions import VerifyMismatchError

from peewee import DoesNotExist
from playhouse.sqlite_ext import SqliteExtDatabase

from src.security import verify_password
from src.models import UserAccount
from src.database import DatabaseSingleton

ACCESS_TOKEN_EXPIRE_MINUTES = 0
SECRET_KEY = "8dacf1b7f32fac1a731b3b6013f0621387e0b60e96e9cc4f1be27a51935ac0f3"
ALGORITHM = "HS256"


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(UserAccount):
    username: str | None = None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserAccount | bool:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user: UserAccount = UserAccount.get(UserAccount.username == token_data.username)  # get user
    # Check if token is stll valid
    if not user.check_token(token):
        raise credentials_exception

    if user is None:
        raise credentials_exception
    return user


def authenticate_user(username: str, password: str) -> UserAccount | bool:
    try:
        user: UserAccount = UserAccount.get(UserAccount.username == username)
        if user and verify_password(user.hashed_password, password):
            return user
    except (VerifyMismatchError, DoesNotExist):
        pass
    return False


async def require_token(current_user: Annotated[UserAccount, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Account Disabled")
    return current_user


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    user.register_token(access_token)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/logout")
async def logout(token: Annotated[str, Depends(oauth2_scheme)], user: Annotated[UserAccount, Depends(require_token)]):
    user.revoke_token(token)
    return {"message": "Logout Successfull"}


@router.get("/logoutall")
async def logoutall(form_data: Annotated[OAuth2PasswordRequestForm, Depends(require_token)]):
    ...
