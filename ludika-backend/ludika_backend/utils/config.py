from pathlib import Path
import ludika_backend
from configparser import ConfigParser

config: ConfigParser | None = None


def get_config_value(section, key):
    """
    Reads a value from the configuration file.

    :param section: The section in the configuration file.
    :param key: The key within the section.
    :return: The value associated with the key in the specified section.
    """
    config = get_config()
    if config.has_option(section, key):
        return config.get(section, key)
    else:
        raise KeyError(f"Key '{key}' not found in section '{section}'.")


def get_config():
    """
    Reads the configuration file and returns a ConfigParser object.
    """
    global config
    if config:
        return config

    config = ConfigParser()
    config_file_path = Path(ludika_backend.__file__).parents[1] / "config.ini"

    if not config_file_path.exists():
        raise FileNotFoundError(f"Configuration file {config_file_path} not found.")

    config.read(config_file_path)
    return config
