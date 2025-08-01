from peewee import SqliteDatabase, CharField, BooleanField, ForeignKeyField, TextField, Model

db = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db


class UserAccount(BaseModel):
    username = CharField(null=False)
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


class Profile(BaseModel):
    parent = ForeignKeyField(UserAccount, backref="profiles")
    name = CharField()
    avatar_url = CharField(null=True)


class Preferences(BaseModel):
    profile = ForeignKeyField(Profile, backref='preferences')
    preferences = TextField()


class Watchlist(BaseModel):
    profile = ForeignKeyField(Profile, backref='watchlists')
    watchlist = TextField()


class Watchhistory(BaseModel):
    profile = ForeignKeyField(Profile, backref='watchhistories')
    watchhistory = TextField()


class Notification(BaseModel):
    profile = ForeignKeyField(Profile, backref='notifications')
    notifications = TextField()


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
