def run_cli():
    from cliss import CLI

    from .tui.app import get_version

    app = CLI(
        name="Siphon-TUI",
        description="Siphon-TUI is a TUI audio/video downloader based on yt-dlp",
        version=get_version(),
    )

    @app.command()
    def config(path: str):
        from .utils.configer import set_path

        print(set_path(path))

    app.run()
