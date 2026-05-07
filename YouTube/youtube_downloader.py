"""YouTube Downloader Script"""

from __future__ import annotations

import datetime
import os
import re
import sys
from pathlib import Path
from typing import Optional, Tuple, List

import pytubefix as pyt  # Library for interacting with YouTube

# Local imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from common import variables as vr
from common import functions as func

banner_yt = vr.banner_yt
banner_title_yt = vr.banner_title_yt


def request_url() -> str:
    """Ask the user for a YouTube URL and validate it with a regex that covers common formats."""
    # Regex covers: youtube.com/watch, youtu.be, embed, shorts, /v/, and preserves the 11-char video ID
    youtube_regex = re.compile(
        r"^(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|v/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})",
        re.IGNORECASE,
    )
    print("-" * 41)
    while True:
        url = input("Please enter the YouTube video URL: ").strip()
        if url and youtube_regex.search(url):
            return url
        print("Please enter a valid YouTube URL.")


def build_and_confirm_yt(url: str, assume_yes: bool = False) -> Tuple[bool, Optional[pyt.YouTube]]:
    """Build a YouTube object from URL, show info, and ask for confirmation.
    Always return a (bool, YouTube|None) tuple.
    """
    try:
        yt = pyt.YouTube(url)  # Build the YouTube object
        title = yt.title
        duration = str(datetime.timedelta(seconds=yt.length))
        channel_title = yt.author
        channel_url = yt.channel_url

        print("-" * 41)
        print(f"Title: {title}")
        print(f"Duration: {duration}")
        print(f"Channel: {channel_title}")
        print(f"Channel URL: {channel_url}")
        print("-" * 41)

        if assume_yes or func.ask_yes_no("Is this the video you want? (y/yes/n/no): "):
            print("-" * 41)
            return True, yt
        return False, None
    except Exception as exc:
        print(f"An error occurred while fetching video details: {exc}")
        return False, None


def get_streams_by_format(yt_video: pyt.YouTube, kind: str):
    """Return streams filtered by the chosen kind: 'audio' | 'video' | 'audio+video' (progressive)."""
    streams = yt_video.streams
    if kind == "audio":
        return streams.filter(only_audio=True)
    if kind == "video":
        return streams.filter(only_video=True, progressive=False)
    if kind == "audio+video":
        return streams.filter(progressive=True)
    raise ValueError(f"Unknown format kind: {kind}")


def display_stream_info(idx: int, stream, kind_label: str) -> None:
    """Pretty-print stream info with safe fallbacks."""
    # File extension
    file_ext = (stream.mime_type.split("/")[-1] if stream.mime_type else "unknown")
    # Codecs
    codecs = getattr(stream, "codecs", None)
    codec = codecs[0] if codecs else "unknown"
    # Resolution & fps for video; abr for audio
    resolution = getattr(stream, "resolution", None) or "N/A"
    fps = getattr(stream, "fps", None) or "N/A"
    abr = getattr(stream, "abr", None) or "N/A"
    # Estimated filesize if available
    size_mb = getattr(stream, "filesize_mb", None)
    size_str = f"{size_mb:.1f} MB" if isinstance(size_mb, float) else "N/A"

    # Build a concise line depending on kind
    if kind_label == "audio":
        extra = f"ABR (Bitrate): {abr}"
    elif kind_label == "video":
        extra = f"Res: {resolution} | FPS: {fps}"
    else:  # progressive audio+video
        extra = f"Res: {resolution} | FPS: {fps}"

    print(f"[{idx}] Type: {kind_label} | Format: {file_ext} | Codec: {codec} | {extra} | Approx size: {size_str}")


def choose_stream(streams, kind_label: str, auto_select: bool = False):
    """List available streams and return the selected stream after confirmation."""
    print("-" * 41)
    print("Available options:\n")
    for i, s in enumerate(streams, start=1):
        display_stream_info(i, s, kind_label)

    print("-" * 41)
    if auto_select:
        return streams[0] if streams else None
    while True:
        selected = input("Select the index of the desired stream: ").strip()
        if not selected.isdigit():
            print("Invalid input. Please enter a number from the list.")
            continue
        index = int(selected)
        if not (1 <= index <= len(streams)):
            print("The selected index does not exist. Please choose another one.")
            continue

        stream = streams[index - 1]
        display_stream_info(index, stream, kind_label)
        if func.ask_yes_no("Please confirm it is the correct stream (y/yes/n/no): "):
            print("-" * 41)
            return stream
        print("-" * 41)


def download_stream(stream, yt_title: str, output_dir: Optional[str] = None) -> bool:
    """Download the selected stream, keeping the extension chosen by pytubefix."""
    download_dir = output_dir if output_dir else func.get_valid_download_directory()
    user_name = input("File name (press Enter to use the video title): ").strip()
    base_name = func.sanitize_filename(user_name if user_name else yt_title)

    try:
        # 1) Let pytubefix choose the right extension (.mp4, .webm, .m4a, ...)
        tmp_path = stream.download(output_path=download_dir)  # <--- no filename!

        # 2) Keep extension chosen by the library
        _, ext = os.path.splitext(tmp_path)  # ext includes leading dot

        final_path = os.path.join(download_dir, f"{base_name}{ext}")
        if tmp_path != final_path:
            os.replace(tmp_path, final_path)

        print(f"Download completed in: {final_path}")
        return True
    except Exception as e:
        print(f"An error occurred during the download: {e}")
        return False


def ask_mode() -> Optional[str]:
    """Ask the user which kind of download they want. Return one of: 'video', 'audio', 'audio+video', 'back'."""
    sel = input(
        "Select the desired option:\n"
        "1 - Download video (no audio).\n"
        "2 - Download audio.\n"
        "3 - Download video (with audio) [progressive <=720p].\n"
        "0 - Select another URL.\n"
        "Selected option: "
    ).strip()
    if sel == "1":
        return "video"
    if sel == "2":
        return "audio"
    if sel == "3":
        return "audio+video"
    if sel == "0":
        return "back"
    print("Invalid option.")
    return None


def ask_another_and_same_url() -> Tuple[bool, bool]:
    """Ask whether the user wants to download another item, and if so, whether from the same URL."""
    other = func.ask_yes_no("Do you want to download another item? (y/yes/n/no): ")
    if not other:
        return False, False
    same = func.ask_yes_no("From the same URL? (y/yes/n/no): ")
    return True, same


def main(
    preset_url: Optional[str] = None,
    output_dir: Optional[str] = None,
    assume_yes: bool = False,
    preset_mode: Optional[str] = None,
) -> int:
    """Main loop: URL loop + per-URL download loop."""
    print(banner_yt)
    print(banner_title_yt)
    print("Welcome to the YouTube Downloader!")
    while True:
        # --- URL loop ---
        url = preset_url if preset_url else request_url()
        if not func.check_url_accessibility(url):
            # If URL is not accessible, restart URL loop
            if preset_url:
                return 1
            continue

        confirmed, yt = build_and_confirm_yt(url, assume_yes=assume_yes)
        if not confirmed or yt is None:
            # User declined or we failed to build the YouTube object; restart URL loop
            if preset_url:
                return 1
            continue

        # --- per-URL loop (allow multiple downloads for this video) ---
        while True:
            kind = preset_mode if preset_mode else ask_mode()
            if kind is None:
                # Invalid option, re-ask inside same URL
                if preset_mode:
                    return 1
                continue
            if kind == "back":
                # Go back to URL loop
                if preset_mode:
                    return 1
                break

            # List and choose streams for the chosen kind
            streams = get_streams_by_format(yt, kind)
            stream = choose_stream(
                streams,
                "audio" if kind == "audio" else ("audio+video" if kind == "audio+video" else "video"),
                auto_select=assume_yes,
            )
            if stream is None:
                print("No streams available for this mode.")
                return 1 if preset_url else 0

            # Download
            if not download_stream(stream, yt.title, output_dir=output_dir):
                return 1 if preset_url else 0

            # Ask whether to download another file and whether from same URL
            if preset_url or assume_yes:
                return 0
            wants_more, same_url = ask_another_and_same_url()
            if not wants_more:
                print("Thanks for using the YouTube Downloader. Returning to the main menu...")
                return 0
            if not same_url:
                # Break per-URL loop to trigger a new URL
                break

        # Back to top of URL loop

    # Unreachable
    # return 0


if __name__ == "__main__":
    main()
