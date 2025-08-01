import src.models


def main():
    src.models.create_tables()
    # config = read_config()
    # if not config:
    #     return
    # file_path = Path(config.get("database_location"))


if __name__ == "__main__":
    main()
