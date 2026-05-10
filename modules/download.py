"""
Async YouTube downloader with progress tracking for Rhythmer.
"""

import asyncio
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional

from yt_dlp import YoutubeDL

AUDIO_CODECS = {"mp3", "aac", "flac", "m4a", "opus", "vorbis", "wav"}
VIDEO_CONTAINER_AUDIO_MAP = {
    "mp4": "m4a",  # H.264 + AAC
    "mov": "m4a",  # H.264 + AAC
    "mkv": "opus",  # VP9 + Opus
    "webm": "opus",  # VP9 + Opus
    "avi": "mp3",  # AVI
    "flv": "aac",  # FLV
}


class DownloadError(Exception):
    pass


class DownloadCancelledError(DownloadError):
    pass


class Download:
    def __init__(
        self,
        url: str,
        codec: str,
        kbps: int,
        download_path: str,
        max_concurrent: int = 3,
    ):
        self.url = url
        self.codec = codec.lower()
        self.kbps = kbps
        self.download_path = download_path
        self.max_concurrent = max_concurrent
        self._cancel_callback: Optional[Callable[[], bool]] = None
        self._cancelled = False
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.is_audio = self.codec in AUDIO_CODECS

        if shutil.which("ffmpeg") is None:
            raise DownloadError(
                "FFmpeg not found in PATH! Please install FFmpeg first."
            )
        if not Path(self.download_path).exists():
            raise DownloadError(f"Download path does not exist: {self.download_path}")

    def set_cancel_check(self, callback: Callable[[], bool]) -> None:
        self._cancel_callback = callback

    def cancel(self) -> None:
        with self._lock:
            self._cancelled = True

    def _get_opts(self) -> dict:
        if self.is_audio:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "nooverwrites": True,
                "format": "bestaudio/best",
                "outtmpl": str(Path(self.download_path) / "%(title)s.%(ext)s"),
                "concurrent_fragment_downloads": self.max_concurrent,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": self.codec,
                        "preferredquality": str(self.kbps),
                    },
                    {"key": "FFmpegMetadata"},
                    {"key": "EmbedThumbnail"},
                ],
            }
            if self.codec == "wav":
                opts["postprocessors"] = [
                    p
                    for p in opts["postprocessors"]
                    if p["key"] not in ["FFmpegMetadata", "EmbedThumbnail"]
                ]
            if self.codec in ["m4a", "aac"]:
                opts["format"] = "bestaudio[ext=m4a]/bestaudio[ext=aac]/bestaudio/best"
                opts["postprocessors"] = [
                    p
                    for p in opts["postprocessors"]
                    if p["key"] != "FFmpegExtractAudio"
                ]
            return opts

        format_str = "bestvideo+bestaudio/best"
        if self.codec in ["mp4", "mov"]:
            format_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/bestvideo+bestaudio/best"
        elif self.codec in ["mkv", "webm"]:
            format_str = "bestvideo[ext=webm]+bestaudio[ext=webm]/bestvideo[ext=webm]+bestaudio/bestvideo+bestaudio/best"

        return {
            "quiet": True,
            "no_warnings": True,
            "nooverwrites": True,
            "format": format_str,
            "outtmpl": str(Path(self.download_path) / "%(title)s.%(ext)s"),
            "concurrent_fragment_downloads": self.max_concurrent,
            "merge_output_format": self.codec,
        }

    def download(self) -> bool:
        self._cancelled = False
        try:
            with YoutubeDL(self._get_opts()) as ydl:
                ydl.download([self.url])
            return True
        except DownloadCancelledError:
            raise
        except Exception as e:
            if self._cancelled or (self._cancel_callback and self._cancel_callback()):
                raise DownloadCancelledError("Download cancelled")
            raise DownloadError(f"Download failed: {str(e)}")

    async def download_async(self) -> bool:
        return await asyncio.get_event_loop().run_in_executor(
            self._executor, self.download
        )

    def __del__(self):
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False, cancel_futures=True)
