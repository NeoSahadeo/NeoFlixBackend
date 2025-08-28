import sys
import yaml

from peewee_migrate import Router
from peewee import SqliteDatabase

from src.models import create_tables, UserAccount
from src.security import hash_password
from src.database import DatabaseSingleton


def read_config() -> dict | None:
    if len(sys.argv) != 2:
        print("Usage: python script.py <config_file.yml>")
        sys.exit(1)
    config_path = sys.argv[1]
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        print("Loaded config:")
        print(config)
        return config
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
    return None


def create_user():
    create_tables()
    UserAccount().create_user("admin", "admin@bromail.com", hash_password("Password1234"))


def migrate():
    router = Router(DatabaseSingleton())

    # Create migration
    router.create('_')

    # Run migration/migrations
    router.run('_')

    # Run all unapplied migrations
    router.run()


# if __name__ == "__main__":
#     migrate()
