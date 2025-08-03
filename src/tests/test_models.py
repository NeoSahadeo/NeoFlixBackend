import pytest
from peewee import DoesNotExist
from src.security import hash_password
from src.models import (
    UserAccount,
    Profile,
    Preferences,
    Watchlist,
    Watchhistory,
    Notification
)


def test_table_creation(db):
    assert UserAccount.table_exists() and Profile.table_exists() and Preferences.table_exists() and Watchlist.table_exists() and Watchhistory.table_exists() and Notification.table_exists()


def test_read_write_delete(db):
    UserAccount().create_user(
        username="Dummy2",
        email="dummy@gmooch.com",
        hashed_password=hash_password("Password@1234")
    )
    assert UserAccount.get(UserAccount.username == "Dummy2")
    u = UserAccount.get(UserAccount.username == "Dummy2")
    assert u.delete_instance() == 1


def test_user_update(db):
    user: UserAccount = UserAccount.get(UserAccount.username == "Dummy1")
    user.update_user("Dummy3", "1234@gmail.com", "password312", False)
    assert UserAccount.get(UserAccount.email == "1234@gmail.com" and UserAccount.username == "Dummy3")


def test_tokens(db):
    user: UserAccount = UserAccount.get(UserAccount.username == "Dummy1")
    user.register_token("cool_tokens")
    assert user.check_token("cool_tokens")

    user.revoke_token("cool_tokens")
    assert not user.check_token("cool_tokens")


def test_profiles(db):
    user: UserAccount = UserAccount.get(UserAccount.username == "Dummy1")
    Profile.create(parent=user, name="Test1")
    assert Profile.get(Profile.name == "Test1")

    profile: Profile = Profile.get(Profile.parent == user, Profile.name == "Test1")
    profile.update_profile("Test2", "")
    assert Profile.get(Profile.name == "Test2")

    profile.delete_instance(recursive=True)
    with pytest.raises(DoesNotExist):
        Profile.get(Profile.name == "Test2")


def test_watchlist(db):
    user: UserAccount = UserAccount.get(UserAccount.username == "Dummy1")
    Profile.create(parent=user, name="Test1")
    assert Profile.get(Profile.name == "Test1")

    profile: Profile = Profile.get(Profile.parent == user, Profile.name == "Test1")
    watchlist: Watchlist = Watchlist.create(profile=profile)

    watchlist.add(2134)
    watchlist.add(9999)
    watchlist.add(0000)
    assert watchlist.watchlist.get("watchlist")[0] == 2134

    watchlist.remove(2134)
    assert len(watchlist.watchlist.get("watchlist")) == 2


def test_watchhistory(db):
    user: UserAccount = UserAccount.get(UserAccount.username == "Dummy1")
    Profile.create(parent=user, name="Test1")
    assert Profile.get(Profile.name == "Test1")

    profile: Profile = Profile.get(Profile.parent == user, Profile.name == "Test1")
    watchhistory: Watchhistory = Watchhistory.create(profile=profile)

    watchhistory.add(2134, 30)
    watchhistory.add(9999, 0)
    watchhistory.add(0000, 0)
    assert watchhistory.watchhistory.get("watchhistory")[0]["id"] == 2134

    watchhistory.remove(2134)
    assert len(watchhistory.watchhistory.get("watchhistory")) == 2


def test_preferences(db):
    user: UserAccount = UserAccount.get(UserAccount.username == "Dummy1")
    Profile.create(parent=user, name="Test1")
    assert Profile.get(Profile.name == "Test1")

    profile: Profile = Profile.get(Profile.parent == user, Profile.name == "Test1")
    preferences: Preferences = Preferences.create(profile=profile)
    preferences.update_prefs({"color": "green"})

    assert preferences.preferences.get("color") == "green"

    preferences.clear()
    assert not preferences.preferences.get("color")


def test_notification(db):
    user: UserAccount = UserAccount.get(UserAccount.username == "Dummy1")
    Profile.create(parent=user, name="Test1")
    assert Profile.get(Profile.name == "Test1")

    profile: Profile = Profile.get(Profile.parent == user, Profile.name == "Test1")
    notification: Notification = Notification.create(profile=profile)

    # notification.add
    ...
