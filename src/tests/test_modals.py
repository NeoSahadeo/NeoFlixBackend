from ..security import hash_password
from ..models import (
    create_tables,
    UserAccount,
    Profile,
    Preferences,
    Watchlist,
    Watchhistory,
    Notification
)


def test_user_creation():
    create_tables()
    assert UserAccount.table_exists() and Profile.table_exists() and Preferences.table_exists() and Watchlist.table_exists() and Watchhistory.table_exists() and Notification.table_exists()


def test_rwd():
    test_user_creation()
    UserAccount.create(
        username="Dummy1",
        email="dummy@gmooch.com",
        hashed_password=hash_password("Password_1234")
    )
    assert UserAccount.get(UserAccount.username == "Dummy1")
    u = UserAccount.get(UserAccount.username == "Dummy1")
    assert u.delete_instance() == 1
