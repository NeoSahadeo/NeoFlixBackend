from pathlib import Path
from utils import read_config
from models import create_tables


def main():
    create_tables()
    # config = read_config()
    # if not config:
    #     return
    # file_path = Path(config.get("database_location"))


if __name__ == "__main__":
    main()
