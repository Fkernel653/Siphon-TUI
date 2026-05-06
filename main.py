from threading import Thread

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    Select,
    Switch,
)

from modules.configer import get_config, set_config

LINES_CODEC = ["M4A", "MP3", "FLAC", "Opus"]
LINES_KBPS = ["320", "256", "128", "64"]


class Rhythmer(App):
    CSS_PATH = "style.tcss"

    def __init__(self):
        super().__init__()
        self.theme = "tokyo-night"
        self.codec = None
        self.kbps = None
        self.download_thread = None
        self.downloading = False
        self.cancelled = False
        self.autosave = True

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main_container"):
            yield Input(id="url_input", placeholder="Enter your URL", type="text")
            yield ProgressBar(id="download_progress", total=100, show_percentage=True)

            with Vertical(classes="select_row"):
                yield Select(
                    ((codec, codec.lower()) for codec in LINES_CODEC),
                    id="codec_select",
                    prompt="Choose a codec",
                )
                with Horizontal(classes="switch_row"):
                    yield Label("Autosave", id="label_switch")
                    yield Switch(id="save_switcher", value=True)
                yield Select(
                    ((kbps, kbps) for kbps in LINES_KBPS),
                    id="kbps_select",
                    prompt="Select a kbps",
                )

            with Horizontal(classes="button_row"):
                yield Button("Download", variant="success", id="accept_button")
                yield Button(
                    "Cancel", variant="error", id="cancel_button", disabled=True
                )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#download_progress", ProgressBar).styles.opacity = 0

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        if event.value is Select.BLANK or event.value is Select.NULL:
            return

        if event.select.id == "codec_select":
            self.codec = str(event.value).lower()
        elif event.select.id == "kbps_select":
            self.kbps = int(event.value)

    @on(Switch.Changed)
    def switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "save_switcher":
            self.autosave = event.value
            if self.autosave:
                if self.codec:
                    set_config("codec", self.codec)
                if self.kbps:
                    set_config("kbps", str(self.kbps))
                self.notify("🔄 Autosave enabled", severity="information")
            else:
                self.notify("⚠️ Autosave disabled", severity="warning")

    @on(Button.Pressed, "#accept_button")
    def action_download(self) -> None:
        url_input = self.query_one("#url_input", Input)
        url = url_input.value.strip()

        if not url:
            self.notify("❌ Please enter a URL", severity="warning")
            return

        if not url.startswith(("http://", "https://")):
            self.notify("❌ Invalid URL", severity="error")
            return

        if not self._validate_settings():
            return

        if self.autosave:
            set_config("codec", self.codec)
            set_config("kbps", str(self.kbps))

        self.cancelled = False
        self.downloading = True
        self.query_one("#accept_button", Button).disabled = True
        self.query_one("#cancel_button", Button).disabled = False
        url_input.disabled = True

        progress = self.query_one("#download_progress", ProgressBar)
        progress.update(total=100, progress=0)
        progress.styles.opacity = 1

        self.notify(f"Downloading {self.codec.upper()} @ {self.kbps}kbps...")

        self.download_thread = Thread(
            target=self._start_download, args=(url,), daemon=True
        )
        self.download_thread.start()

    @on(Button.Pressed, "#cancel_button")
    def action_cancel(self) -> None:
        if self.downloading:
            self.cancelled = True
            self.notify("Cancelling...", severity="warning")
        else:
            self._download_complete(True, "Nothing to cancel")

    def update_progress(self, value: int) -> None:
        if not self.cancelled:
            self.call_from_thread(self._update_progress_ui, value)

    def _update_progress_ui(self, value: int) -> None:
        try:
            progress = self.query_one("#download_progress", ProgressBar)
            progress.update(progress=value)
        except Exception:
            pass

    def check_cancelled(self) -> bool:
        return self.cancelled

    def _start_download(self, url: str) -> None:
        from modules.download import Download, DownloadCancelledError, DownloadError

        try:
            downloader = Download(url=url, codec=self.codec, kbps=self.kbps)
            downloader.set_progress_callback(self.update_progress)
            downloader.set_cancel_check(self.check_cancelled)

            success = downloader.download()

            if success:
                self.call_from_thread(
                    self._download_complete, True, "Download completed!"
                )
            else:
                self.call_from_thread(self._download_complete, False, "Download failed")

        except DownloadCancelledError:
            self.call_from_thread(self._download_complete, False, "Download cancelled")
        except DownloadError as e:
            self.call_from_thread(self._download_complete, False, str(e))
        except Exception as e:
            self.call_from_thread(self._download_complete, False, f"Error: {e}")

    def _download_complete(self, success: bool, message: str) -> None:
        self.downloading = False
        self.download_thread = None
        self.cancelled = False

        accept_button = self.query_one("#accept_button", Button)
        cancel_button = self.query_one("#cancel_button", Button)
        url_input = self.query_one("#url_input", Input)

        accept_button.disabled = False
        cancel_button.disabled = True
        url_input.disabled = False
        url_input.value = ""
        url_input.focus()

        emoji = "✅" if success else "❌"
        self.notify(
            f"{emoji} {message}", severity="information" if success else "error"
        )

        self.set_timer(3, self._hide_progress)

    def _hide_progress(self) -> None:
        try:
            progress = self.query_one("#download_progress", ProgressBar)
            progress.update(progress=0)
            progress.styles.opacity = 0
        except Exception:
            pass

    def _validate_settings(self) -> bool:
        if self.codec is None:
            saved_codec = get_config("codec")
            if saved_codec:
                self.codec = saved_codec

        if self.kbps is None:
            saved_kbps = get_config("kbps")
            if saved_kbps:
                self.kbps = int(saved_kbps)

        if not self.codec and not self.kbps:
            self.notify(
                "❌ Please select a codec format and bitrate (kbps)", severity="warning"
            )
            return False
        elif not self.codec:
            self.notify("❌ Please select a codec format", severity="warning")
            return False
        elif not self.kbps:
            self.notify("❌ Please select a bitrate (kbps)", severity="warning")
            return False
        return True

    def on_unmount(self) -> None:
        self.cancelled = True


if __name__ == "__main__":
    try:
        Rhythmer().run()
    except KeyboardInterrupt:
        import sys

        from modules.colors import GREEN, RESET

        print(f"\n{GREEN}Goodbye!{RESET}")
        sys.exit(0)
