from peewee import SqliteDatabase
import threading


class DatabaseSingleton:
    _instance: SqliteDatabase = None
    _lock = threading.Lock()

    def __new__(cls, db_name='database.db'):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = SqliteDatabase(db_name)
        return cls._instance

    @classmethod
    def initialize(cls, db_name):
        if cls._instance:
            cls._instance.close()
        cls._instance = SqliteDatabase(db_name)
        return cls._instance
