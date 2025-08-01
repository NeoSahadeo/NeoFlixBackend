import threading
from playhouse.sqlite_ext import SqliteExtDatabase


class DatabaseSingleton:
    _instance: SqliteExtDatabase = None
    _lock = threading.Lock()

    def __new__(cls, db_name='database.db'):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = SqliteExtDatabase(db_name, pragmas=(
                        ('cache_size', -1024 * 64),  # 64MB page-cache.
                        ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!).
                        ('foreign_keys', 1)))  # Enforce foreign-key constraints.
        return cls._instance

    @classmethod
    def initialize(cls, db_name):
        if cls._instance:
            cls._instance.close()
        cls._instance = SqliteExtDatabase(db_name, pragmas=(
            ('cache_size', -1024 * 64),  # 64MB page-cache.
            ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!).
            ('foreign_keys', 1)))  # Enforce foreign-key constraints.
        return cls._instance
