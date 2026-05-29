import json
import sys
from pathlib import Path

from color_kiss.utils import error, success
from platformdirs import user_config_dir

CONFIG_DIR = Path(user_config_dir("Siphon"))
CONFIG_FILE = CONFIG_DIR / "config.json"
HOME_PATH = str(Path.home())

KEY_NAME = "path"


def set_path(path: str) -> str:
    """
    Manage download directory storage.
    - With path: saves to config.json
    - Without path: displays current config
    """
    try:
        input_path = Path(path).expanduser().resolve()
        if not input_path.is_dir():
            sys.exit(error("Please enter the correct path!"))

        path_str = str(input_path)

        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({KEY_NAME: path_str}, f, ensure_ascii=False, indent=4)

        return success(f"\nPath: {path_str}\nConfig file: {CONFIG_FILE}")
    except PermissionError:
        return error(f"\nPermission denied! Cannot write to {CONFIG_FILE}")
    except OSError as e:
        return error(f"\nError saving configuration: {e}")


def get_path() -> tuple[str, str | None]:
    """
    Read download path from config.json.
    Returns (path, error_message).
    If error_message is None, path is valid.
    """
    if not CONFIG_FILE.exists():
        return HOME_PATH, None

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        if not config or KEY_NAME not in config:
            return HOME_PATH, "Download path not set in config"

        path = config[KEY_NAME]
        if not Path(path).is_dir():
            return HOME_PATH, f"Download path does not exist: {path}"

        return path, None
    except (json.JSONDecodeError, FileNotFoundError):
        return HOME_PATH, "Config file is corrupted! Run: siphon-tui set /path"
