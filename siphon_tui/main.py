def main():
    import sys

    from color_kiss import GREEN, RESET
    from color_kiss.utils import error

    if len(sys.argv) <= 1:
        from .tui.app import run_tui

        try:
            run_tui()
        except KeyboardInterrupt:
            print(f"{GREEN}Goodbye!{RESET}")
            sys.exit(0)
        except Exception as e:
            sys.exit(error(str(e)))
    else:
        from .cli import run_cli

        try:
            run_cli()
        except KeyboardInterrupt:
            print(f"{GREEN}Goodbye!{RESET}")
            sys.exit(0)
        except Exception as e:
            sys.exit(error(str(e)))
