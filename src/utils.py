import sys
import yaml


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
