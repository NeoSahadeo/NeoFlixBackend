import pytest
from src.database import DatabaseSingleton
from src.security import hash_password
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
        hashed_password=hash_password("Password_1234")
    )
    return _db


def test_table_creation(db):
    assert UserAccount.table_exists() and Profile.table_exists() and Preferences.table_exists() and Watchlist.table_exists() and Watchhistory.table_exists() and Notification.table_exists()


def test_read_write_delete(db):
    UserAccount().create_user(
        username="Dummy1",
        email="dummy@gmooch.com",
        hashed_password=hash_password("Password_1234")
    )
    assert UserAccount.get(UserAccount.username == "Dummy1")
    u = UserAccount.get(UserAccount.username == "Dummy1")
    assert u.delete_instance() == 1


def test_user_update(db):
    user: UserAccount = UserAccount.get(UserAccount.username == "Dummy1")
    user.update_user("Dummy2", "1234@gmail.com", "password312", False)
    assert UserAccount.get(UserAccount.email == "1234@gmail.com" and UserAccount.username == "Dummy2")
