from threading import Thread

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Select

from siphon_tui.utils.configer import get_path

AUDIO_CODECS = ["M4A", "MP3", "FLAC", "Opus", "Vorbis", "WAV"]
VIDEO_CONTAINERS = ["MP4", "MKV", "WebM", "MOV", "AVI", "FLV"]
LINES_KBPS = ["320", "256", "128", "64"]

VIDEO_CONTAINER_AUDIO_MAP = {
    "mp4": "m4a",
    "mov": "m4a",
    "mkv": "opus",
    "webm": "opus",
    "avi": "mp3",
    "flv": "aac",
}

SELECT_IDS = {
    "codec": "audio_codec_select",
    "container": "video_container_select",
    "kbps": "kbps_select",
}


def get_version() -> str:
    """Get version from installed package metadata."""
    try:
        from importlib.metadata import version

        return version("Siphon-TUI")
    except Exception:
        return "unknown"


class SiphonTUI(App):
    CSS_PATH = "style.tcss"

    def __init__(self):
        super().__init__()
        self.theme = "rose-pine"
        self.codec = None
        self.container = None
        self.kbps = 256

        path, error_msg = get_path()
        self.download_path = path

        self.downloading = False
        self.cancelled = False
        self._path_error = error_msg

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main_container"):
            yield Input(id="url_input", placeholder="Enter your URL", type="text")
            with Vertical(id="select_section"):
                with Horizontal(id="codecs_row"):
                    yield Select(
                        ((c, c.lower()) for c in AUDIO_CODECS),
                        id=SELECT_IDS["codec"],
                        prompt="Audio codec",
                    )
                    yield Select(
                        ((c, c.lower()) for c in VIDEO_CONTAINERS),
                        id=SELECT_IDS["container"],
                        prompt="Container (optional)",
                    )
                yield Select(
                    ((k, k) for k in LINES_KBPS),
                    id=SELECT_IDS["kbps"],
                    prompt="Bitrate (kbps)",
                )
            with Horizontal(id="button_row"):
                yield Button("Download", variant="success", id="accept_button")
                yield Button(
                    "Cancel", variant="error", id="cancel_button", disabled=True
                )
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Siphon-TUI"
        self.sub_title = f"v{get_version()}"

        if self._path_error:
            self.notify(
                f"⚠️ {self._path_error}\nUsing: {self.download_path}",
                severity="warning",
                timeout=10,
            )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        if event.value in (Select.BLANK, Select.NULL):
            setattr(
                self,
                {
                    "audio_codec_select": "codec",
                    "video_container_select": "container",
                    "kbps_select": "kbps",
                }[event.select.id],
                None,
            )
            return

        if event.select.id == SELECT_IDS["codec"]:
            self.codec = str(event.value).lower()
        elif event.select.id == SELECT_IDS["container"]:
            self.container = str(event.value).lower()
            if self.container:
                audio_codec = VIDEO_CONTAINER_AUDIO_MAP.get(self.container)
                if audio_codec:
                    self.codec = audio_codec
                    codec_select = self.query_one(f"#{SELECT_IDS['codec']}", Select)
                    for option in codec_select._options:
                        if (
                            option[1] not in (Select.BLANK, Select.NULL)
                            and str(option[1]).lower() == audio_codec
                        ):
                            codec_select.value = option[1]
                            break
        elif event.select.id == SELECT_IDS["kbps"]:
            self.kbps = int(event.value)

    @on(Button.Pressed, "#accept_button")
    def action_download(self) -> None:
        url = self.query_one("#url_input", Input).value.strip()
        if not url:
            return self.notify("❌ Please enter a URL", severity="warning")
        if not url.startswith(("http://", "https://")):
            return self.notify("❌ Invalid URL", severity="error")
        if not self._validate_settings():
            return

        self.cancelled = False
        self.downloading = True
        self.query_one("#accept_button", Button).disabled = True
        self.query_one("#cancel_button", Button).disabled = False
        self.query_one("#url_input", Input).disabled = True

        msg = (
            f"⬇️ Downloading {self.codec.upper()} -> {self.container.upper()} @ {self.kbps}kbps..."
            if self.container
            else f"⬇️ Downloading {self.codec.upper()} @ {self.kbps}kbps (audio only)..."
        )
        self.notify(msg)

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
            self.notify("Nothing to cancel", severity="warning")
            self._reset_ui()

    def _start_download(self, url: str) -> None:
        from siphon_tui.utils.download import (
            Download,
            DownloadCancelledError,
            DownloadError,
        )

        try:
            downloader = Download(
                url=url,
                codec=self.container or self.codec,
                kbps=self.kbps,
                download_path=self.download_path,
            )
            downloader.set_cancel_check(lambda: self.cancelled)
            downloader.download()
            self.call_from_thread(
                self._download_complete,
                True,
                f"Download completed on {self.download_path}",
            )
        except DownloadCancelledError:
            self.call_from_thread(self._download_complete, False, "Download cancelled")
        except DownloadError as e:
            self.call_from_thread(self._download_complete, False, str(e))
        except Exception as e:
            self.call_from_thread(self._download_complete, False, f"Error: {e}")

    def _download_complete(self, success: bool, message: str) -> None:
        self.downloading = False
        self.cancelled = False
        self._reset_ui()
        self.notify(
            f"{'✅' if success else '❌'} {message}",
            severity="information" if success else "error",
        )

    def _reset_ui(self) -> None:
        self.query_one("#accept_button", Button).disabled = False
        self.query_one("#cancel_button", Button).disabled = True
        url_input = self.query_one("#url_input", Input)
        url_input.disabled = False
        url_input.value = ""
        url_input.focus()

    def _validate_settings(self) -> bool:
        if self.container:
            if not self.codec:
                self.notify(
                    "❌ Failed to set audio codec for container", severity="error"
                )
                return False
        elif not self.codec:
            codec_select = self.query_one(f"#{SELECT_IDS['codec']}", Select)
            if codec_select.value not in (Select.BLANK, Select.NULL):
                self.codec = str(codec_select.value).lower()
            else:
                self.notify(
                    "❌ Please select audio codec or video container",
                    severity="warning",
                )
                return False
        self.kbps = self.kbps or 256
        return True


def run_tui():
    app = SiphonTUI()
    app.run()
