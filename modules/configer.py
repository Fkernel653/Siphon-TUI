import json
from pathlib import Path


def set_path(path: str) -> bool:
    """
    Write download path to config.json.
    Returns True if successful, False otherwise.
    """
    config_file = Path(__file__).parent.parent / "config.json"

    config = {"path": path}

    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


def get_path() -> str:
    """
    Read download path from config.json.
    Returns the path or error if not found.
    """
    from modules.colors import RED, RESET

    config_file = Path(__file__).parent.parent / "config.json"
    default_path = Path.home()

    if not config_file.exists():
        return str(default_path)

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config["path"]
    except (json.JSONDecodeError, FileNotFoundError):
        exit(f"{RED}Config file is corrupted! Run: python add_path.py{RESET}")
