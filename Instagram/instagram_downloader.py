"""Instagram downloader module."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import instaloader

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from common import functions as func
from common import variables as vr

banner_instagram = vr.banner_instagram
separator = vr.separator


def get_instagram_url() -> str:
    """Prompt the user for a valid Instagram URL."""
    instagram_url_pattern = re.compile(r"^https?://(www\.)?instagram\.com/.+", re.IGNORECASE)
    while True:
        url = input("Please enter the Instagram URL: ").strip()
        if not url:
            print("The URL cannot be empty. Please enter a valid Instagram URL.")
            continue
        if instagram_url_pattern.match(url):
            return url
        print("Invalid Instagram URL. Please try again.")


def extract_shortcode(url: str) -> str:
    """Extract the Instagram shortcode from the post URL."""
    parts = [part for part in url.strip("/").split("/") if part]
    if not parts:
        raise ValueError("Invalid Instagram URL.")
    return parts[-1]


def build_target_stem(download_dir: str, requested_name: str, shortcode: str, ext: str) -> str:
    """Build a non-conflicting path stem for Instaloader downloads."""
    base_name = func.sanitize_filename(requested_name) if requested_name else shortcode
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


def download_instagram_post(url: str) -> bool:
    """Download an Instagram post (image or video)."""
    loader = instaloader.Instaloader(save_metadata=False, download_comments=False)

    try:
        shortcode = extract_shortcode(url)
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        download_dir = func.get_valid_download_directory()
        requested_name = input("Enter the file name (press Enter for default name): ").strip()

        extension = ".mp4" if post.is_video else ".jpg"
        output_stem = build_target_stem(download_dir, requested_name, shortcode, extension)
        media_url = post.video_url if post.is_video else post.url
        loader.download_pic(filename=output_stem, url=media_url, mtime=post.date_local)
        print(f"Download completed in: {download_dir}")
        return True
    except (ValueError, IndexError) as exc:
        print(f"Invalid Instagram URL format. Reason: {exc}")
        return False
    except Exception as exc:
        print(f"The Instagram post is not reachable. Reason: {exc}")
        return False


def main() -> int:
    """Run the Instagram downloader flow."""
    print(banner_instagram)
    print("Welcome to the Instagram Downloader")
    print(separator)
    while True:
        url = get_instagram_url()
        if not func.check_url_accessibility(url):
            continue
        if download_instagram_post(url):
            return 0
        return 1


if __name__ == "__main__":
    main()
