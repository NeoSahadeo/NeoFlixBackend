from peewee import CharField, BooleanField, ForeignKeyField, Model
from playhouse.sqlite_ext import JSONField
from src.database import DatabaseSingleton

db = DatabaseSingleton()


class BaseModel(Model):
    class Meta:
        database = db


class UserAccount(BaseModel):
    username = CharField(unique=True, null=False)
    email = CharField(unique=True, null=False)
    disabled = BooleanField(default=False, null=False)
    hashed_password = CharField(null=False)

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


class Profile(BaseModel):
    parent = ForeignKeyField(UserAccount, backref="profiles")
    name = CharField()
    avatar_url = CharField(null=True)


class Preferences(BaseModel):
    profile = ForeignKeyField(Profile, backref='preferences')
    preferences = JSONField()


class Watchlist(BaseModel):
    profile = ForeignKeyField(Profile, backref='watchlists')
    preferences = JSONField()


class Watchhistory(BaseModel):
    profile = ForeignKeyField(Profile, backref='watchhistories')
    preferences = JSONField()


class Notification(BaseModel):
    profile = ForeignKeyField(Profile, backref='notifications')
    preferences = JSONField()


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
