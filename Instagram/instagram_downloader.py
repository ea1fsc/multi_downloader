"""Instagram downloader module."""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import instaloader

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from common import functions as func
from common import variables as vr

banner_instagram = vr.banner_instagram
banner_title_instagram = vr.banner_title_instagram

# Shared with app/adapters/instagram_adapter.py. Post paths are checked later by extract_shortcode.
INSTAGRAM_URL_REGEX = re.compile(r"^https?://(www\.)?instagram\.com/.+", re.IGNORECASE)


def is_valid_instagram_url(url: str) -> bool:
    return bool(url and INSTAGRAM_URL_REGEX.match(url.strip()))


def get_instagram_url() -> str:
    """Prompt the user for a valid Instagram URL."""
    while True:
        url = input("Please enter the Instagram URL: ").strip()
        if not url:
            print("The URL cannot be empty. Please enter a valid Instagram URL.")
            continue
        if is_valid_instagram_url(url):
            return url
        print("Invalid Instagram URL. Please try again.")


def extract_shortcode(url: str) -> str:
    """Extract the Instagram shortcode from the post URL."""
    parsed = urlparse(url.strip())
    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) < 2 or path_parts[0].lower() not in {"p", "reel", "tv"}:
        raise ValueError("Instagram URL must include /p/, /reel/ or /tv/.")
    shortcode = path_parts[1]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", shortcode):
        raise ValueError("Invalid shortcode in Instagram URL.")
    return shortcode


def build_target_stem(download_dir: str, requested_name: str, shortcode: str, ext: str) -> str:
    """Build a non-conflicting path stem for Instaloader downloads."""
    base_name = func.sanitize_filename(func.strip_extension(requested_name, ext)) if requested_name else shortcode
    if not base_name:
        base_name = shortcode

    full_path = os.path.join(download_dir, f"{base_name}{ext}")
    if not os.path.exists(full_path):
        return os.path.splitext(full_path)[0]

    path_without_ext, _ = os.path.splitext(full_path)
    counter = 1
    while os.path.exists(f"{path_without_ext}_{counter}{ext}"):
        counter += 1
    return f"{path_without_ext}_{counter}"


def extension_from_content_type(content_type: str | None, default_ext: str) -> str:
    """'.webp' for 'image/webp; charset=x', '.jpg' for image/jpeg; ``default_ext`` if not image/video."""
    mime = (content_type or "").split(";")[0].strip().lower()
    main_type, _, subtype = mime.partition("/")
    if main_type not in ("image", "video") or not re.fullmatch(r"[a-z0-9.+-]+", subtype):
        return default_ext
    return "." + subtype.replace("jpeg", "jpg")


def download_media(
    loader: instaloader.Instaloader,
    media_url: str,
    download_dir: str,
    requested_name: str,
    shortcode: str,
    mtime,
    default_ext: str,
) -> str:
    """Download ``media_url`` and return the real saved path.

    Instaloader's download_pic picks the extension from the Content-Type (e.g. '.webp')
    and silently skips when that file exists, so the path is decided here instead: the
    extension comes from the response and the name is made unique for that extension.
    """
    resp = loader.context.get_raw(media_url)
    ext = extension_from_content_type(resp.headers.get("Content-Type"), default_ext)
    # A typed "name.jpg" must not become "name.jpg.webp".
    requested = func.strip_extension(requested_name, default_ext) if requested_name else ""
    path = build_target_stem(download_dir, requested, shortcode, ext) + ext
    try:
        loader.context.write_raw(resp, path)
    finally:
        # write_raw streams into "<path>.temp" and leaves it behind if the transfer fails.
        if os.path.exists(path + ".temp"):
            os.remove(path + ".temp")
    os.utime(path, (time.time(), mtime.timestamp()))
    return path


def download_instagram_post(url: str, output_dir: str | None = None) -> bool:
    """Download an Instagram post (image or video)."""
    loader = instaloader.Instaloader(save_metadata=False, download_comments=False)

    try:
        shortcode = extract_shortcode(url)
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        download_dir = output_dir if output_dir else func.get_valid_download_directory()
        requested_name = input("Enter the file name (press Enter for default name): ").strip()

        extension = ".mp4" if post.is_video else ".jpg"
        media_url = post.video_url if post.is_video else post.url
        saved = download_media(loader, media_url, download_dir, requested_name, shortcode, post.date_local, extension)
        print(f"Download completed in: {saved}")
        return True
    except (ValueError, IndexError) as exc:
        print(f"Invalid Instagram URL format. Reason: {exc}")
        return False
    except Exception as exc:
        error_message = str(exc)
        if "403" in error_message:
            print(
                "The Instagram post metadata request was blocked (HTTP 403). "
                "This usually happens when Instagram rate-limits anonymous requests. "
                "Try again later, use a different post URL, or configure an authenticated Instaloader session."
            )
        else:
            print(f"The Instagram post is not reachable. Reason: {exc}")
        return False


def main(
    preset_url: str | None = None,
    output_dir: str | None = None,
    assume_yes: bool = False,
) -> int:
    """Run the Instagram downloader flow."""
    print(banner_instagram)
    print(banner_title_instagram)
    print("Welcome to the Instagram Downloader!")
    while True:
        print("-" * 41)
        url = preset_url if preset_url else get_instagram_url()
        if preset_url and not is_valid_instagram_url(url):
            print(f"Invalid Instagram URL: {url}")
            return 1
        if not func.check_url_accessibility(url):
            if preset_url:
                return 1
            continue
        if download_instagram_post(url, output_dir=output_dir):
            if preset_url:
                return 0
            if not assume_yes and not func.ask_yes_no(
                "Do you want to download another Instagram post? (y/yes/n/no): "
            ):
                print("Thanks for using the Instagram Downloader. Returning to the main menu...")
                return 0
            if assume_yes:
                return 0
            continue
        if preset_url:
            return 1
        if not assume_yes and not func.ask_yes_no(
            "Do you want to try another Instagram URL? (y/yes/n/no): "
        ):
            return 1
        if assume_yes:
            return 1


if __name__ == "__main__":
    main()
