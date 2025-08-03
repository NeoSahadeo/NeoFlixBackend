import datetime

import pydantic

from peewee import CharField, BooleanField, ForeignKeyField, Model
from playhouse.sqlite_ext import JSONField

from argon2.exceptions import VerifyMismatchError

from src.security import hash_password, verify_password
from src.database import DatabaseSingleton
from src.serializers import serialize_datetime

db = DatabaseSingleton()


class BaseModel(Model):
    class Meta:
        database = db


class UserAccount(BaseModel):
    username = CharField(unique=True, null=False)
    email = CharField(unique=True, null=False)
    disabled = BooleanField(default=False, null=False)
    hashed_password = CharField(null=False)

    tokens = JSONField(null=False, default={
        "tokens": []
    })

    def create_user(self, username, email, hashed_password, disabled=False):
        UserAccount.create(
            username=username,
            email=email,
            hashed_password=hashed_password,
            disabled=disabled
        )

    def delete_user(self, email):
        self.delete()

    def update_user(self, username, email, hashed_password, disabled):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.disabled = disabled
        self.save()

    def register_token(self, token: str):
        self.tokens.get("tokens").append([
            hash_password(token),
            serialize_datetime(datetime.datetime.now())
        ])
        self.save()

    def check_token(self, token: str) -> bool:
        for t, d in self.tokens.get("tokens"):
            try:
                if verify_password(t, token):
                    return True
            except VerifyMismatchError:
                pass
        return False

    def revoke_token(self, token: str):
        for i, [t, d] in enumerate(self.tokens.get("tokens")):
            try:
                if verify_password(t, token):
                    self.tokens.get("tokens").pop(i)
                    self.save()
                    return
            except VerifyMismatchError:
                pass

    def revoke_all_tokens(self):
        self.tokens = {"tokens": []}
        self.save()


class Profile(BaseModel):
    parent = ForeignKeyField(UserAccount, backref="profiles", null=False)
    name = CharField()
    avatar_url = CharField(null=True)

    @classmethod
    def create(cls, **query):
        inst = super().create(**query)

        Preferences.create(profile=inst, preferences={})
        Watchlist.create(profile=inst, watchlist={})
        Watchhistory.create(profile=inst, watchhistory={})
        Notification.create(profile=inst, notifications={})
        return inst

    class Meta:
        indexes = (
            (('parent', 'name'), True),
        )

    def update_profile(self, name, avatar_url):
        self.name = name or self.name
        self.avatar_url = avatar_url or self.avatar_url
        self.save()


class Preferences(BaseModel):
    profile = ForeignKeyField(Profile, backref='preferences')
    preferences = JSONField()


class Watchlist(BaseModel):
    profile = ForeignKeyField(Profile, backref='watchlists')
    watchlist = JSONField(default={"watchlist": []}, null=False)

    def add(self, tmdb_id):
        if self.watchlist.get("watchlist"):
            self.watchlist.get("watchlist").append(tmdb_id)
        else:
            self.watchlist = {"watchlist": [tmdb_id]}
        self.save()

    def remove(self, tmdb_id):
        watchlist = self.watchlist.get("watchlist")
        if watchlist:
            filtered_watchlist = [id for id in watchlist if id != tmdb_id]
            self.watchlist = {"watchlist": filtered_watchlist}
            self.save()

    def clear(self):
        self.watchlist = {"watchlist": []}
        self.save()


class Watchhistory(BaseModel):
    profile = ForeignKeyField(Profile, backref='watchhistories')
    watchhistory = JSONField(default={"watchhistory": []}, null=False)

    def add(self, tmdb_id, current_time):
        if self.watchhistory.get("watchhistory"):
            self.watchhistory.get("watchhistory").append({
                "id": tmdb_id,
                "current_time": current_time
            })
        else:
            self.watchhistory = {"watchhistory": [{
                "id": tmdb_id,
                "current_time": current_time
            }]}
        self.save()

    def remove(self, tmdb_id):
        watchhistory = self.watchhistory.get("watchhistory")
        if watchhistory:
            filtered_watchhistory = [entry for entry in watchhistory if entry["id"] != tmdb_id]
            self.watchhistory = {"watchhistory": filtered_watchhistory}
            self.save()


class Notification(BaseModel):
    profile = ForeignKeyField(Profile, backref='notifications')
    notifications = JSONField()


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(UserAccount):
    username: str | None = None


def create_tables():
    db.connect()
    db.create_tables([
        UserAccount,
        Profile,
        Preferences,
        Watchlist,
        Watchhistory,
        Notification,
    ])
    db.close()
