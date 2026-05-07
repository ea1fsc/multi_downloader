"""Instagram operations for the application layer."""

from __future__ import annotations

import os
import re
from typing import Callable

import instaloader

from app.domain.errors import DownloadError, ValidationError
from Instagram.instagram_downloader import build_target_stem, extract_shortcode

INSTAGRAM_URL_REGEX = re.compile(r"^https?://(www\.)?instagram\.com/.+", re.IGNORECASE)


def is_valid_instagram_url(url: str) -> bool:
    return bool(url and INSTAGRAM_URL_REGEX.match(url.strip()))


def preview_post(url: str) -> dict:
    """Load post metadata for preview (may raise)."""
    loader = instaloader.Instaloader(save_metadata=False, download_comments=False)
    shortcode = extract_shortcode(url)
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    return {
        "shortcode": shortcode,
        "caption": post.caption[:200] + "…" if post.caption and len(post.caption) > 200 else post.caption,
        "is_video": post.is_video,
        "owner": post.owner_username,
    }


def download_post(
    url: str,
    output_dir: str,
    filename_stem: str | None,
    cancel_event,
    on_progress: Callable[[float | None, str], None] | None = None,
) -> str:
    if cancel_event is not None and cancel_event.is_set():
        raise DownloadError("Download cancelled.")

    loader = instaloader.Instaloader(save_metadata=False, download_comments=False)
    try:
        shortcode = extract_shortcode(url)
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc
    except Exception as exc:
        raise DownloadError(f"Could not load Instagram post: {exc}") from exc

    if not os.path.isdir(output_dir):
        raise ValidationError(f"Invalid output directory: {output_dir}")
    if not os.access(output_dir, os.W_OK):
        raise ValidationError(f"Directory is not writable: {output_dir}")

    extension = ".mp4" if post.is_video else ".jpg"
    requested = filename_stem.strip() if filename_stem else ""
    output_stem = build_target_stem(output_dir, requested, shortcode, extension)
    media_url = post.video_url if post.is_video else post.url

    if on_progress:
        on_progress(None, "Downloading media…")
    try:
        loader.download_pic(filename=output_stem, url=media_url, mtime=post.date_local)
    except Exception as exc:
        err = str(exc)
        if "403" in err:
            raise DownloadError(
                "Instagram blocked the request (HTTP 403). Try again later or use an authenticated session."
            ) from exc
        raise DownloadError(f"Instagram download failed: {exc}") from exc

    final_file = output_stem + extension
    if on_progress:
        on_progress(1.0, f"Saved: {final_file}")
    return final_file
