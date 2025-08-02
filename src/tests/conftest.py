import pytest
from src.security import hash_password
from src.database import DatabaseSingleton
from src.models import (
    UserAccount,
    Profile,
    Preferences,
    Watchlist,
    Watchhistory,
    Notification
)


@pytest.fixture
def db():
    _db = DatabaseSingleton.initialize(":memory:")
    _db.bind([UserAccount, Profile, Preferences, Watchlist, Watchhistory, Notification], bind_refs=False, bind_backrefs=False)
    _db.connect()
    _db.create_tables([
        UserAccount,
        Profile,
        Preferences,
        Watchlist,
        Watchhistory,
        Notification
    ])
    UserAccount().create_user(
        username="Dummy1",
        email="test_dummy@gmooch.com",
        hashed_password=hash_password("Password@1234")
    )

    yield _db
    _db.drop_tables([
        UserAccount,
        Profile,
        Preferences,
        Watchlist,
        Watchhistory,
        Notification
    ])
    _db.close()
