"""Twitter/X operations for the application layer."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import yt_dlp

from app.domain.errors import DownloadError
# URL patterns live with the CLI module so both paths accept the same URLs.
from Twitter.twitter_downloader import TWITTER_URL_REGEX, build_output_template, is_valid_twitter_url  # noqa: F401


def fetch_info(url: str) -> dict | None:
    opts: dict = {"quiet": True, "skip_download": True, "noplaylist": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as exc:
        raise DownloadError(f"Could not fetch post details: {exc}") from exc


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
    """Download best video+audio; returns the saved file path (directory if unknown)."""

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
    saved_files: list[str] = []
    opts: dict = {
        "outtmpl": build_output_template(download_dir, base_name),
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "progress_hooks": [_hook],
        "post_hooks": [saved_files.append],  # final path, after merging
        "quiet": True,
        "no_warnings": True,
    }
    try:
        if on_progress:
            on_progress(0.0, "Starting download…")
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        saved = saved_files[-1] if saved_files else str(download_dir)
        if on_progress:
            on_progress(1.0, f"Saved: {saved}")
        return saved
    except KeyboardInterrupt as exc:
        raise DownloadError("Download cancelled.") from exc
    except Exception as exc:
        raise DownloadError(f"Download failed: {exc}") from exc
