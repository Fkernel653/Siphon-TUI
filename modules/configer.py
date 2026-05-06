import json
from pathlib import Path
from typing import Any


def get_config(item: str, default: Any = None) -> Any:
    """
    Read a value from config.json.
    Returns the value or default if not found.

    Usage:
        path = get_config("path")
        codec = get_config("codec", "mp3")
    """
    config_file = Path(__file__).parent.parent / "config.json"

    if not config_file.exists():
        return default

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get(item, default)
    except (json.JSONDecodeError, FileNotFoundError):
        return default


def set_config(item: str, value: Any) -> bool:
    """
    Write a value to config.json (keeps existing keys).
    Returns True if successful, False otherwise.

    Usage:
        set_config("codec", "mp3")
        set_config("kbps", "320")
    """
    config_file = Path(__file__).parent.parent / "config.json"

    if not config_file.exists():
        return False

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        config = {}

    config[item] = value

    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


def get_full_config() -> dict:
    """
    Read the entire config.json.
    Returns the full config dict or empty dict if not found.
    """
    config_file = Path(__file__).parent.parent / "config.json"

    if not config_file.exists():
        return {}

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}
