"""
Async YouTube audio downloader with progress tracking.
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from shutil import which
from typing import Any, Callable, Dict, Optional

from yt_dlp import YoutubeDL

from modules.configer import get_config


class DownloadError(Exception):
    pass


class DownloadCancelledError(DownloadError):
    pass


class Download:
    """Async YouTube audio downloader with progress tracking."""

    def __init__(
        self,
        url: str,
        codec: str,
        kbps: int,
        max_concurrent: int = 3,
    ):
        self.url = url
        self.codec = codec
        self.kbps = kbps
        self.max_concurrent = max_concurrent

        self.saved_path = get_config("path", (str(Path.home() / "Music")))
        self.saved_codec = get_config("codec", self.codec)
        self.saved_kbps = get_config("kbps", str(self.kbps))

        self._progress_callback: Optional[Callable[[int], None]] = None
        self._cancel_callback: Optional[Callable[[], bool]] = None
        self._cancelled = False
        self._lock = threading.Lock()
        self._last_progress = 0
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent)

        # Validate requirements
        if which("ffmpeg") is None:
            raise DownloadError("FFmpeg not found in PATH!")

    def set_progress_callback(self, callback: Callable[[int], None]) -> None:
        """Set callback for progress updates (0-100)."""
        self._progress_callback = callback

    def set_cancel_check(self, callback: Callable[[], bool]) -> None:
        """Set callback to check if download should be cancelled."""
        self._cancel_callback = callback

    def cancel(self) -> None:
        """Cancel the current download."""
        with self._lock:
            self._cancelled = True

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """Progress hook for yt-dlp."""
        if self._cancelled or (self._cancel_callback and self._cancel_callback()):
            raise DownloadCancelledError("Download cancelled")

        if not self._progress_callback:
            return

        status = d.get("status", "")

        if status == "downloading":
            # Try to get percentage from yt-dlp first
            percent_str = d.get("_percent_str", "0%")
            if percent_str and percent_str != "N/A":
                try:
                    percent = float(percent_str.rstrip("%"))
                except (ValueError, AttributeError):
                    percent = 0
            else:
                # Fallback to manual calculation
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                percent = (downloaded / total * 100) if total > 0 else 0

            # Map downloading phase to 0-90% to leave room for processing
            progress = int(min(percent * 0.9, 90))

            with self._lock:
                if progress > self._last_progress:
                    self._last_progress = progress
                    self._progress_callback(progress)

        elif status == "processing":
            with self._lock:
                if self._last_progress < 95:
                    self._last_progress = 95
                    self._progress_callback(95)

        elif status == "finished":
            with self._lock:
                if self._last_progress < 100:
                    self._last_progress = 100
                    self._progress_callback(100)

    def _get_opts(self) -> dict:
        """Get yt-dlp options."""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "nooverwrites": True,
            "noprogress": False,
            "progress_hooks": [self._progress_hook],
            "format": "bestaudio/best",
            "outtmpl": str(Path(self.saved_path) / "%(title)s.%(ext)s"),
            "concurrent_fragment_downloads": self.max_concurrent,
            "embedmetadata": True,
            "writethumbnail": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.saved_codec,
                    "preferredquality": self.saved_kbps,
                },
                {"key": "FFmpegMetadata"},
                {"key": "EmbedThumbnail"},
            ],
        }

        return opts

    def download(self) -> bool:
        """Download audio from URL. Returns True if successful."""
        self._cancelled = False
        self._last_progress = 0

        opts = self._get_opts()

        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([self.url])

            if self._progress_callback:
                self._progress_callback(100)
            return True

        except DownloadCancelledError:
            raise
        except Exception as e:
            if self._cancelled:
                raise DownloadCancelledError("Download cancelled")
            raise DownloadError(f"Download failed: {e}")

    async def download_async(self) -> bool:
        """Async wrapper for download."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.download)

    async def download_all(self, urls: list[str]) -> list[tuple[str, bool, str]]:
        """Download multiple URLs concurrently."""
        sem = asyncio.Semaphore(self.max_concurrent)

        async def download_one(url: str) -> tuple[str, bool, str]:
            async with sem:
                downloader = Download(
                    url=url,
                    codec=self.saved_codec,
                    kbps=self.saved_kbps,
                    max_concurrent=1,
                )
                downloader._executor = self._executor

                if self._progress_callback:
                    downloader.set_progress_callback(self._progress_callback)
                if self._cancel_callback:
                    downloader.set_cancel_check(self._cancel_callback)

                try:
                    await downloader.download_async()
                    return (url, True, "")
                except DownloadCancelledError:
                    return (url, False, "Download cancelled")
                except DownloadError as e:
                    return (url, False, str(e))
                except Exception as e:
                    return (url, False, f"Unexpected error: {e}")

        tasks = [download_one(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

    def __del__(self):
        """Cleanup executor on deletion."""
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False, cancel_futures=True)
