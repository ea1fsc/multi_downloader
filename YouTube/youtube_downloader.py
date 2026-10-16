"""YouTube Downloader Script"""

from __future__ import annotations

import datetime
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Callable, Optional, Tuple, List

import pytubefix as pyt  # Library for interacting with YouTube

# Local imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from common import variables as vr
from common import functions as func

banner_yt = vr.banner_yt
banner_title_yt = vr.banner_title_yt

# Shared with app/adapters/youtube_adapter.py. Covers watch, youtu.be, embed, /v/, shorts
# and live on www., m. and music. hosts; group 1 is the 11-char video ID.
YOUTUBE_URL_REGEX = re.compile(
    r"^(?:https?://)?(?:(?:www|m|music)\.)?"
    r"(?:youtube\.com/(?:watch\?v=|embed/|v/|shorts/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})",
    re.IGNORECASE,
)


def is_valid_youtube_url(url: str) -> bool:
    return bool(url and YOUTUBE_URL_REGEX.search(url.strip()))


def request_url() -> str:
    """Ask the user for a YouTube URL and validate it."""
    print("-" * 41)
    while True:
        url = input("Please enter the YouTube video URL: ").strip()
        if is_valid_youtube_url(url):
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


# pytubefix's default client (VISION_OS in 11.x) returns no progressive streams.
# These clients list them (typically only itag 18, 360p), but YouTube answers 403
# for some of them (ANDROID_VR, MWEB as of 2026-10), so each one is checked.
PROGRESSIVE_FALLBACK_CLIENTS = ("ANDROID", "ANDROID_VR", "MWEB")


def _has_usable_progressive(yt_video: pyt.YouTube) -> bool:
    """True when a progressive stream is listed and its URL answers (HEAD for the size)."""
    stream = yt_video.streams.filter(progressive=True).first()
    if stream is None:
        return False
    try:
        stream.filesize  # HEAD request; 403 means YouTube blocks this client's stream URLs
    except Exception:  # noqa: BLE001
        return False
    return True


def with_progressive_streams(url: str, yt_video: pyt.YouTube) -> pyt.YouTube:
    """Return ``yt_video`` or, if it has no usable progressive stream, a fallback-client copy that has one.

    Callers must download from the returned object: stream URLs and itags are client-specific.
    """
    if _has_usable_progressive(yt_video):
        return yt_video
    for client in PROGRESSIVE_FALLBACK_CLIENTS:
        try:
            candidate = pyt.YouTube(url, client=client)
            if _has_usable_progressive(candidate):
                return candidate
        except Exception:  # noqa: BLE001 — a failing fallback client just means "try the next one"
            continue
    return yt_video


def stream_size_mb(stream) -> float | None:
    """Approximate size in MB, or None when unknown (the size lookup is an HTTP request that can fail)."""
    try:
        size_mb = getattr(stream, "filesize_mb", None)
    except Exception:  # noqa: BLE001
        return None
    return size_mb if isinstance(size_mb, float) else None


def _leading_number(value) -> float:
    """Parse the leading number of values like '128kbps' or '1080p'; 0 when missing."""
    match = re.match(r"^(\d+(?:\.\d+)?)", str(value or ""))
    return float(match.group(1)) if match else 0.0


def _stream_quality_key(stream, kind: str) -> tuple[float, float]:
    """Sort key: bitrate for audio, resolution then fps for video."""
    if kind == "audio":
        return (_leading_number(getattr(stream, "abr", None)), 0.0)
    return (
        _leading_number(getattr(stream, "resolution", None)),
        _leading_number(getattr(stream, "fps", None)),
    )


def get_streams_by_format(yt_video: pyt.YouTube, kind: str) -> list:
    """Return streams for 'audio' | 'video' | 'audio+video' (progressive), best quality first."""
    streams = yt_video.streams
    if kind == "audio":
        filtered = streams.filter(only_audio=True)
    elif kind == "video":
        filtered = streams.filter(only_video=True, progressive=False)
    elif kind == "audio+video":
        filtered = streams.filter(progressive=True)
    else:
        raise ValueError(f"Unknown format kind: {kind}")
    return sorted(filtered, key=lambda s: _stream_quality_key(s, kind), reverse=True)


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
    size_mb = stream_size_mb(stream)
    size_str = f"{size_mb:.1f} MB" if size_mb is not None else "N/A"

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


def stream_extension(stream, fallback_path: str = "") -> str:
    """Return the file extension (with dot) matching the stream's real container.

    pytubefix names every audio-only stream '.m4a', even WebM/Opus ones, so the
    extension is derived from the MIME type instead of the library's filename.
    """
    mime_type = getattr(stream, "mime_type", None) or ""
    if "/" in mime_type:
        main_type, subtype = mime_type.split("/", 1)
        if main_type == "audio" and subtype == "mp4":
            return ".m4a"
        if subtype:
            return f".{subtype}"
    return os.path.splitext(fallback_path)[1]


def final_file_stem(base_name: str, ext: str) -> str:
    """File stem for ``ext``: no duplicated extension and never empty."""
    return func.sanitize_filename(func.strip_extension(base_name, ext)) or "youtube_media"


def download_stream_to(
    stream,
    directory: str,
    base_name: str,
    interrupt_checker: Optional[Callable[[], bool]] = None,
) -> Optional[str]:
    """Download ``stream`` to ``<directory>/<base_name><ext>``; return that path, or None if interrupted.

    pytubefix's default target is ``<video title>.<ext>`` in ``directory``, opened with "wb",
    which silently replaced any user file with that name. The data goes to a unique hidden
    temp file instead, which is moved into place only when complete and removed otherwise.
    """
    ext = stream_extension(stream)
    final_path = os.path.join(directory, f"{final_file_stem(base_name, ext)}{ext}")
    # Not tempfile.mkstemp: it creates the file 0600 and the download would keep that mode.
    tmp_name = f".multi-downloader-{uuid.uuid4().hex}.part"
    tmp_path = os.path.join(directory, tmp_name)
    try:
        written = stream.download(
            output_path=directory,
            filename=tmp_name,
            skip_existing=False,
            interrupt_checker=interrupt_checker,
        )
        if written is None:
            return None
        os.replace(tmp_path, final_path)
        return final_path
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def download_stream(stream, yt_title: str, output_dir: Optional[str] = None) -> bool:
    """Download the selected stream, naming it with the extension of its real container."""
    download_dir = output_dir if output_dir else func.get_valid_download_directory()
    user_name = input("File name (press Enter to use the video title): ").strip()
    base_name = func.sanitize_filename(user_name if user_name else yt_title)

    try:
        final_path = download_stream_to(stream, download_dir, base_name)
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
        if preset_url and not is_valid_youtube_url(url):
            print(f"Invalid YouTube URL: {url}")
            return 1
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
            source = with_progressive_streams(url, yt) if kind == "audio+video" else yt
            streams = get_streams_by_format(source, kind)
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
