"""Entry point for python -m siphon_tui."""

import sys

from color_kiss import GREEN
from color_kiss.utils import error, styled


def main():
    try:
        if len(sys.argv) <= 1:
            from .tui.app import run_tui

            run_tui()
        else:
            from .cli import run_cli

            run_cli()
    except KeyboardInterrupt:
        print(styled("\nGoodbye!", GREEN))
        sys.exit(0)
    except Exception as e:
        sys.exit(error(str(e)))


if __name__ == "__main__":
    main()
