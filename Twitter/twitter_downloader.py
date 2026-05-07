"""Twitter/X downloader module."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

import yt_dlp

# Local imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from common import variables as vr
from common import functions as func

banner_twitter = vr.banner_twitter
banner_title_twitter = vr.banner_title_twitter


def request_twitter_url() -> str:
    """Ask the user for a Twitter/X URL and validate it."""
    twitter_regex = re.compile(
        r"^https?://(www\.)?(twitter\.com|x\.com)/[^/\s]+/status/\d+",
        re.IGNORECASE,
    )
    print("-" * 41)
    while True:
        url = input("Please enter the Twitter/X post URL: ").strip()
        if url and twitter_regex.search(url):
            return url
        print("Please enter a valid Twitter/X status URL.")


def get_tweet_info(url: str) -> Optional[dict]:
    """Fetch tweet metadata with yt-dlp without downloading."""
    opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as e:
        print(f"An error occurred while fetching post details: {e}")
        return None


def confirm_tweet(info: dict) -> bool:
    """Show tweet info and ask for confirmation."""
    title = info.get("title", "N/A")
    uploader = info.get("uploader", "N/A")
    duration = info.get("duration")
    like_count = info.get("like_count")

    print("-" * 41)
    print(f"Title: {title}")
    print(f"Author: {uploader}")
    if duration is not None:
        print(f"Duration: {duration} seconds")
    if like_count is not None:
        print(f"Likes: {like_count}")
    print("-" * 41)

    return func.ask_yes_no("Is this the post you want to download? (y/yes/n/no): ")


def download_tweet_video(
    url: str,
    info: dict,
    output_dir: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """Download the best video+audio stream from a tweet."""
    download_dir = Path(output_dir) if output_dir else Path(func.get_valid_download_directory())
    suggested_name = func.sanitize_filename(info.get("title") or "twitter_video")
    custom_name = input(
        "File name (press Enter to use the default post title): "
    ).strip()
    base_name = func.sanitize_filename(custom_name) if custom_name else suggested_name
    if not base_name:
        base_name = "twitter_video"

    output_template = str(download_dir / f"{base_name}.%(ext)s")
    opts = {
        "outtmpl": output_template,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        return True, str(download_dir)
    except Exception as e:
        print(f"An error occurred during the download: {e}")
        return False, None


def ask_download_another() -> bool:
    """Ask if user wants to download another tweet."""
    return func.ask_yes_no("Do you want to download another Twitter/X post? (y/yes/n/no): ")


def main(
    preset_url: Optional[str] = None,
    output_dir: Optional[str] = None,
    assume_yes: bool = False,
) -> int:
    """Main loop for Twitter/X downloads."""
    print(banner_twitter)
    print(banner_title_twitter)
    print("Welcome to the Twitter/X Downloader!")
    while True:
        url = preset_url if preset_url else request_twitter_url()
        if not func.check_url_accessibility(url):
            if preset_url:
                return 1
            continue

        info = get_tweet_info(url)
        if not info:
            if preset_url:
                return 1
            continue

        # Twitter posts can be text-only; ensure there is downloadable media.
        if info.get("ext") is None and not info.get("formats"):
            print("This post does not seem to contain downloadable media.")
            if preset_url:
                return 1
            continue

        if not assume_yes and not confirm_tweet(info):
            if preset_url:
                return 1
            continue

        ok, download_path = download_tweet_video(url, info, output_dir=output_dir)
        if ok:
            print("-" * 41)
            print(f"Download completed in: {download_path}")
            if preset_url:
                return 0
        elif preset_url:
            return 1

        if preset_url or assume_yes:
            return 0 if ok else 1

        if not ask_download_another():
            print("Thanks for using the Twitter/X Downloader. Returning to the main menu...")
            return 0


if __name__ == "__main__":
    main()
