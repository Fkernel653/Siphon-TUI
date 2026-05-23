def run_cli():
    import sys

    from cliss import CLI
    from color_kiss.utils import error

    from .tui.app import get_version

    app = CLI(
        name="Siphon-TUI",
        description="Siphon-TUI is a TUI audio/video downloader based on yt-dlp",
        version=get_version(),
    )

    @app.command()
    def config(path: str):
        """Configure the application settings path.

        Sets the configuration directory path for storing application
        settings and data files.

        Args:
            path: Directory path where configuration files will be stored.

        Raises:
            SystemExit: If configuration operation fails.
        """
        try:
            from .utils.configer import set_path

            print(set_path(path))
        except Exception as e:
            sys.exit(error(str(e)))

    app.run()
