"""Twitter/X operations for the application layer."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import yt_dlp

from app.domain.errors import DownloadError, ValidationError

TWITTER_URL_REGEX = re.compile(
    r"^https?://(www\.)?(twitter\.com|x\.com)/[^/\s]+/status/\d+",
    re.IGNORECASE,
)


def is_valid_twitter_url(url: str) -> bool:
    return bool(url and TWITTER_URL_REGEX.search(url.strip()))


def fetch_info(url: str) -> dict | None:
    opts: dict = {"quiet": True, "skip_download": True, "noplaylist": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception:
        return None


def ensure_downloadable(info: dict | None) -> None:
    if not info:
        raise DownloadError("Could not fetch post details.")
    if info.get("ext") is None and not info.get("formats"):
        raise DownloadError("This post does not contain downloadable media.")


def download_tweet(
    url: str,
    info: dict,
    output_dir: str,
    base_name: str,
    cancel_event,
    on_progress: Callable[[float | None, str], None] | None = None,
) -> str:
    """Download best video+audio; returns directory path (files inside)."""

    def _hook(d: dict) -> None:
        if cancel_event is not None and cancel_event.is_set():
            raise KeyboardInterrupt("Cancelled")
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes") or 0
            if total and int(total) > 0:
                frac = min(1.0, int(downloaded) / int(total))
                if on_progress:
                    on_progress(frac, "Downloading…")
            elif on_progress:
                on_progress(None, "Downloading…")
        elif status == "finished" and on_progress:
            on_progress(1.0, "Post-processing…")

    download_dir = Path(output_dir)
    download_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(download_dir / f"{base_name}.%(ext)s")
    opts: dict = {
        "outtmpl": output_template,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "progress_hooks": [_hook],
        "quiet": True,
        "no_warnings": True,
    }
    try:
        if on_progress:
            on_progress(0.0, "Starting download…")
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        if on_progress:
            on_progress(1.0, f"Completed in: {output_dir}")
        return str(download_dir)
    except KeyboardInterrupt as exc:
        raise DownloadError("Download cancelled.") from exc
    except Exception as exc:
        raise DownloadError(f"Download failed: {exc}") from exc
