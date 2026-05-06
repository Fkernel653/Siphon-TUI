from pathlib import Path

from modules.colors import BLUE, BOLD, GREEN, RED, RESET, YELLOW
from modules.configer import get_config, set_config


def add_path():
    """Configure or display the download directory path"""
    try:
        user_input = input(f"{BOLD}\tEnter your path: {RESET}").strip()

        # Setter mode - user provided a path
        if user_input:
            input_path = Path(user_input).expanduser().resolve()

            if not input_path.exists():
                try:
                    input_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    return f"{RED}Error creating directory: {e}{RESET}"

            # Save path to config file
            if set_config("path", str(input_path)):
                config_file = Path(__file__).parent / "config.json"
                return "\n".join(
                    [
                        f"{GREEN}Configuration saved successfully!{RESET}",
                        f"{YELLOW}    Path: {RESET}{input_path}",
                        f"{BLUE}    Config file: {RESET}{config_file}",
                    ]
                )
            else:
                return f"{RED}Failed to save configuration!{RESET}"

        # Getter mode - no input provided, show current config
        else:
            saved_path_str = get_config("path")

            if saved_path_str:
                saved_path = Path(saved_path_str)

                # Verify the saved path still exists
                if saved_path.exists():
                    config_file = Path(__file__).parent / "config.json"
                    return "\n".join(
                        [
                            f"{GREEN}Current download directory: {RESET}{saved_path}",
                            f"{GREEN}Configuration file: {RESET}{config_file}",
                        ]
                    )
                else:
                    return "\n".join(
                        [
                            f"{RED}Config file exists but the saved path is invalid!{RESET}",
                            f"{RED}Path: {RESET}{saved_path}",
                        ]
                    )
            else:
                return f"{RED}Config file not found! Please set a download path first.{RESET}"

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        return f"\r\033[K\n{GREEN}Goodbye!{RESET}"

    except Exception as e:
        return f"{RED}Error: {e}{RESET}"


if __name__ == "__main__":
    print(add_path())
