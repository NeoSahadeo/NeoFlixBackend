from datetime import datetime, timedelta, timezone
from typing import Annotated
import os

from dotenv import load_dotenv

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer


import jwt
from jwt.exceptions import InvalidTokenError

from argon2.exceptions import VerifyMismatchError

from peewee import DoesNotExist, IntegrityError

from src.security import verify_password
from src.models import UserAccount, Profile, Token, TokenData, Watchlist, Watchhistory
from src.forms import CreateProfileForm, DeleteProfileForm, UpdateProfileForm, UpdateWatchlistForm, UpdateWatchHistoryForm

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 525960  # minutes in a year
ALGORITHM = "HS256"
SECRET_KEY = os.getenv("PRIVATE_JWT_SECRET")

TMDB_API_KEY = os.getenv("PRIVATE_TMDB_API_KEY")


access_router = APIRouter(tags=["Access"])
manageprofiles_router = APIRouter(prefix="/manageprofiles", tags=["Manage Profile"])
watchlist_router = APIRouter(prefix="/watchlist", tags=["Watchlist"])
watchhistory_router = APIRouter(prefix="/watchhistory", tags=["Watch History"])
notification_router = APIRouter(prefix="/notification", tags=["Notification"])
preferences_router = APIRouter(prefix="/preferences", tags=["Preferences"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


def local_get_profile(id, user: UserAccount):
    try:
        profile: Profile = Profile.get(Profile.parent == user, Profile.id == id)
        return profile
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not profile found")


@access_router.post("/token")
async def generate_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
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


@access_router.get("/tmdb_apikey")
async def tmdb_apikey(_: Annotated[str, Depends(require_token)]):
    return Token(access_token=TMDB_API_KEY, token_type="bearer")


@access_router.get("/logout")
async def logout(token: Annotated[str, Depends(oauth2_scheme)], user: Annotated[UserAccount, Depends(require_token)]):
    user.revoke_token(token)
    return {"message": "Logout Successfull"}


@access_router.get("/logoutall")
async def logoutall(user: Annotated[UserAccount, Depends(require_token)]):
    user.revoke_all_tokens()
    return {"message": "Logouts Successfull"}


@manageprofiles_router.get("/{id}")
async def get_profile(id: int, user: Annotated[UserAccount, Depends(require_token)]):
    try:
        profile: Profile = local_get_profile(id, user)
        return {"data": profile.__data__}
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id does not match known profiles")


@manageprofiles_router.get("")
async def get_all_profiles(user: Annotated[UserAccount, Depends(require_token)]):
    try:
        profiles = Profile.select().where(Profile.parent_id == user.id)
        return {"data": [profile.__data__ for profile in profiles]}
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id does not match known profiles")


@manageprofiles_router.post("")
async def create_profile(token: Annotated[str, Depends(oauth2_scheme)],
                         user: Annotated[UserAccount, Depends(require_token)],
                         form_data: Annotated[CreateProfileForm, Depends()]):
    try:
        profile: Profile = Profile.create(parent=user, name=form_data.name, avatar_url=form_data.avatar_url)
        return {"message": "Profile created successfully", "data": profile.__data__}
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile with name already exists")


@manageprofiles_router.delete("")
async def delete_profile(token: Annotated[str, Depends(oauth2_scheme)],
                         user: Annotated[UserAccount, Depends(require_token)],
                         form_data: Annotated[DeleteProfileForm, Depends()]):
    profile: Profile = local_get_profile(form_data.id, user)
    profile.delete_instance(recursive=True)
    return {"message": "Profile deleted successfully", "data": profile.__data__}


@manageprofiles_router.put("")
async def update_profile(token: Annotated[str, Depends(oauth2_scheme)],
                         user: Annotated[UserAccount, Depends(require_token)],
                         form_data: Annotated[UpdateProfileForm, Depends()]):
    profile: Profile = local_get_profile(form_data.id, user)
    try:
        profile.update_profile(form_data.name, form_data.avatar_url)
        return {"message": "Profile updated successfully", "data": profile.__data__}
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile with name already exists")


@watchlist_router.get("/{profile_id}")
async def get_watchlist(profile_id: int, user: Annotated[UserAccount, Depends(require_token)]):
    profile: Profile = local_get_profile(profile_id, user)
    watchlist: Watchlist = Watchlist.get(Watchlist.profile == profile)
    return {"data": watchlist.__data__.get("watchlist")}


@watchlist_router.put("/add")
async def add_watchlist(profile_id: int,
                        user: Annotated[UserAccount, Depends(require_token)],
                        form_data: Annotated[UpdateWatchlistForm, Depends()]):
    profile: Profile = local_get_profile(profile_id, user)
    watchlist: Watchlist = Watchlist.get(Watchlist.profile == profile)
    watchlist.add(form_data.tmdb_id)
    return {"data": watchlist.__data__.get("watchlist")}


@watchlist_router.put("/remove")
async def remove_watchlist(profile_id: int,
                           user: Annotated[UserAccount, Depends(require_token)],
                           form_data: Annotated[UpdateWatchlistForm, Depends()]):
    profile: Profile = local_get_profile(profile_id, user)
    watchlist: Watchlist = Watchlist.get(Watchlist.profile == profile)
    watchlist.remove(form_data.tmdb_id)
    return {"data": watchlist.__data__.get("watchlist")}


@watchlist_router.put("/clear")
async def clear_watchlist(profile_id: int, user: Annotated[UserAccount, Depends(require_token)]):
    profile: Profile = local_get_profile(profile_id, user)
    watchlist: Watchlist = Watchlist.get(Watchlist.profile == profile)
    watchlist.clear()
    return {"data": watchlist.__data__.get("watchlist")}


@watchhistory_router.get("/{profile_id}")
async def get_watchhistory(profile_id: int,
                           user: Annotated[UserAccount, Depends(require_token)]):
    profile: Profile = local_get_profile(profile_id, user)
    watchhistory: Watchhistory = Watchhistory.get(Watchhistory.profile == profile)
    return {"data": watchhistory.__data__.get("watchhistory")}


@watchhistory_router.put("/add")
async def add_watchhistory(profile_id: int,
                           user: Annotated[UserAccount, Depends(require_token)],
                           form_data: Annotated[UpdateWatchHistoryForm, Depends()]):
    profile: Profile = local_get_profile(profile_id, user)
    watchhistory: Watchhistory = Watchhistory.get(Watchhistory.profile == profile)
    watchhistory.add(form_data.tmdb_id, form_data.current_time)
    return {"data": watchhistory.__data__.get("watchhistory")}


@watchhistory_router.put("/remove")
async def remove_watchhistory(profile_id: int,
                              tmdb_id: int,
                              user: Annotated[UserAccount, Depends(require_token)]):
    profile: Profile = local_get_profile(profile_id, user)
    watchhistory: Watchhistory = Watchhistory.get(Watchhistory.profile == profile)
    watchhistory.remove(tmdb_id)
    return {"data": watchhistory.__data__.get("watchhistory")}


@watchhistory_router.put("/clear")
async def clear_watchhistory(profile_id: int, user: Annotated[UserAccount, Depends(require_token)]):
    profile: Profile = local_get_profile(profile_id, user)
    watchhistory: Watchhistory = Watchhistory.get(Watchhistory.profile == profile)
    watchhistory.clear()
    return {"data": watchhistory.__data__.get("watchhistory")}


# @notification_router.get("/{profile_id}")
# async def get_notification(profile_id: int,
#                            user: Annotated[UserAccount, Depends(require_token)]):
#     profile: Profile = local_get_profile(profile_id, user)
#     watchhistory: Watchhistory = Watchhistory.get(Watchhistory.profile == profile)
#     return {"data": watchhistory.__data__.get("watchhistory")}
