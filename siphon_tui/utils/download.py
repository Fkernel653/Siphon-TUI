"""
Sync YouTube downloader with cancellation support for Rhythmer TUI.
"""

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

AUDIO_CODECS = frozenset({"mp3", "aac", "flac", "m4a", "opus", "vorbis", "wav"})

VIDEO_CONTAINER_AUDIO_MAP = {
    "mp4": "m4a",
    "mov": "m4a",
    "mkv": "opus",
    "webm": "opus",
    "avi": "mp3",
    "flv": "aac",
}


class DownloadError(Exception):
    pass


class DownloadCancelledError(DownloadError):
    pass


@dataclass
class Download:
    """Synchronous audio/video downloader using yt-dlp with cancellation support."""

    url: str
    codec: str
    kbps: int
    download_path: str
    max_concurrent: int = 3

    _cancel_callback: Optional[Callable[[], bool]] = field(default=None, repr=False)
    _cancelled: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        """Validate inputs on instantiation."""
        self.codec = self.codec.lower()
        self.is_audio = self.codec in AUDIO_CODECS

        if shutil.which("ffmpeg") is None:
            raise DownloadError(
                "FFmpeg not found in PATH! Please install FFmpeg first."
            )
        if not Path(self.download_path).exists():
            raise DownloadError(f"Download path does not exist: {self.download_path}")

    def set_cancel_check(self, callback: Callable[[], bool]) -> None:
        """Set a callback that returns True if download should be cancelled."""
        self._cancel_callback = callback

    def cancel(self) -> None:
        """Mark the download as cancelled."""
        self._cancelled = True

    def _check_cancelled(self) -> bool:
        """Check if download has been cancelled via callback or flag."""
        if self._cancelled:
            return True
        if self._cancel_callback and self._cancel_callback():
            self._cancelled = True
            return True
        return False

    def _get_opts(self) -> dict[str, Any]:  # type: ignore[explicit-any]
        """Build yt-dlp options dict based on codec type (audio or video)."""
        base_opts = {
            "quiet": True,
            "no_warnings": True,
            "nooverwrites": True,
            "outtmpl": str(Path(self.download_path) / "%(title)s.%(ext)s"),
            "concurrent_fragment_downloads": self.max_concurrent,
        }

        if self.is_audio:
            base_opts["format"] = "bestaudio/best"
            base_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.codec,
                    "preferredquality": str(self.kbps),
                },
                {"key": "FFmpegMetadata"},
                {"key": "EmbedThumbnail"},
            ]

            if self.codec == "wav":
                base_opts["postprocessors"] = [
                    p
                    for p in base_opts["postprocessors"]
                    if p["key"] not in ["FFmpegMetadata", "EmbedThumbnail"]
                ]
            elif self.codec in {"m4a", "aac"}:
                base_opts["format"] = (
                    "bestaudio[ext=m4a]/bestaudio[ext=aac]/bestaudio/best"
                )
                base_opts["postprocessors"] = [
                    p
                    for p in base_opts["postprocessors"]
                    if p["key"] != "FFmpegExtractAudio"
                ]
        else:
            audio_ext = VIDEO_CONTAINER_AUDIO_MAP.get(self.codec, "m4a")
            format_str = (
                f"bestvideo[ext=mp4]+bestaudio[ext={audio_ext}]/bestvideo+bestaudio/best"
                if self.codec == "mp4"
                else f"bestvideo+bestaudio[ext={audio_ext}]/bestvideo+bestaudio/best"
            )
            base_opts.update(format=format_str, merge_output_format=self.codec)

        return base_opts

    def download(self) -> None:
        """Download a single URL synchronously. Raises DownloadError or DownloadCancelledError."""
        if self._check_cancelled():
            raise DownloadCancelledError("Download was cancelled before starting")

        try:
            from yt_dlp import YoutubeDL

            with YoutubeDL(self._get_opts()) as ydl:  # type: ignore[explicit-any]
                ydl.download([self.url])
        except Exception as e:
            if self._cancelled:
                raise DownloadCancelledError("Download was cancelled") from e
            raise DownloadError(f"Download failed: {e}") from e
