from pathlib import Path

from modules.colors import BLUE, BOLD, GREEN, RED, RESET, YELLOW
from modules.configer import set_path


def add_path():
    """configure or display the download directory path"""
    try:
        user_input = input(f"{BOLD}\tEnter your path: {RESET}").strip()

        if user_input:
            input_path = Path(user_input)

            if not input_path.is_dir():
                return f"{RED}Please enter the correct path!{RESET}"

            # Save path to config file
            if set_path(str(input_path)):
                config_file = Path(__file__).parent / "config.json"
                return (
                    f"{GREEN}configuration saved successfully!\n{YELLOW}Path: {RESET}{input_path}\n{BLUE}config file: {RESET}{config_file}",
                )
            else:
                return f"{RED}Failed to save configuration!{RESET}"

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        return f"\r\033[K\n{GREEN}Goodbye!{RESET}"

    except Exception as e:
        return f"{RED}Error: {e}{RESET}"


if __name__ == "__main__":
    print(add_path())
