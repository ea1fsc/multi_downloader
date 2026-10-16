"""YouTube operations for the application layer (non-interactive)."""

from __future__ import annotations

import datetime
import re
from typing import Callable

import pytubefix as pyt

from app.domain.errors import DownloadError, ValidationError
from app.domain.models import StreamOption, YoutubeKind
from common import functions as func
# URL patterns live with the CLI module so both paths accept the same URLs.
from YouTube.youtube_downloader import YOUTUBE_URL_REGEX, is_valid_youtube_url, stream_size_mb  # noqa: F401


def load_video(url: str, kind: YoutubeKind | None = None) -> pyt.YouTube:
    """Load a video; for progressive mode, use a client that offers progressive streams.

    Analysis and download must pass the same ``kind`` so both see the same client's streams.
    """
    from YouTube.youtube_downloader import with_progressive_streams

    if not is_valid_youtube_url(url):
        raise ValidationError("Please enter a valid YouTube URL.")
    try:
        yt = pyt.YouTube(url)
        return with_progressive_streams(url, yt) if kind == YoutubeKind.AUDIO_VIDEO else yt
    except Exception as exc:
        raise DownloadError(f"Could not load video details: {exc}") from exc


def preview_dict(yt: pyt.YouTube) -> dict:
    duration = str(datetime.timedelta(seconds=yt.length))
    return {
        "title": yt.title,
        "duration": duration,
        "channel": yt.author,
        "channel_url": yt.channel_url,
    }


def kind_to_label(kind: YoutubeKind) -> str:
    if kind == YoutubeKind.AUDIO:
        return "audio"
    if kind == YoutubeKind.VIDEO:
        return "video"
    return "audio+video"


def _stream_label(idx: int, stream, kind_label: str) -> str:
    file_ext = stream.mime_type.split("/")[-1] if stream.mime_type else "unknown"
    codecs = getattr(stream, "codecs", None)
    codec = codecs[0] if codecs else "unknown"
    resolution = getattr(stream, "resolution", None) or "N/A"
    fps = getattr(stream, "fps", None) or "N/A"
    abr = getattr(stream, "abr", None) or "N/A"
    size_mb = stream_size_mb(stream)
    size_str = f"{size_mb:.1f} MB" if size_mb is not None else "N/A"
    if kind_label == "audio":
        extra = f"ABR (Bitrate): {abr}"
    else:
        extra = f"Res: {resolution} | FPS: {fps}"
    return f"Type: {kind_label} | Format: {file_ext} | Codec: {codec} | {extra} | Approx size: {size_str}"


def _parse_resolution_height(resolution: str | None) -> int | None:
    if not resolution:
        return None
    match = re.match(r"^(\d+)", resolution)
    if not match:
        return None
    return int(match.group(1))


def _parse_abr_kbps(abr: str | None) -> float | None:
    if not abr:
        return None
    match = re.match(r"^(\d+(?:\.\d+)?)", abr)
    if not match:
        return None
    return float(match.group(1))


def list_streams_for_kind(yt: pyt.YouTube, kind: YoutubeKind) -> list[StreamOption]:
    from YouTube.youtube_downloader import get_streams_by_format

    kind_str = (
        "audio"
        if kind == YoutubeKind.AUDIO
        else ("audio+video" if kind == YoutubeKind.AUDIO_VIDEO else "video")
    )
    streams = list(get_streams_by_format(yt, kind_str))
    label_kind = "audio" if kind == YoutubeKind.AUDIO else ("audio+video" if kind == YoutubeKind.AUDIO_VIDEO else "video")
    options: list[StreamOption] = []
    for i, s in enumerate(streams, start=1):
        codecs = getattr(s, "codecs", None)
        codec = codecs[0] if codecs else None
        resolution = getattr(s, "resolution", None)
        fps = getattr(s, "fps", None)
        abr = getattr(s, "abr", None)
        size_mb = stream_size_mb(s)
        options.append(
            StreamOption(
                index=i,
                label=_stream_label(i, s, label_kind),
                kind=kind,
                codec=codec,
                size_mb=size_mb,
                resolution=resolution,
                resolution_height=_parse_resolution_height(resolution),
                fps=int(fps) if isinstance(fps, int) else None,
                abr=abr,
                abr_kbps=_parse_abr_kbps(abr),
                itag=getattr(s, "itag", None),
            )
        )
    return options


def get_stream_by_index(yt: pyt.YouTube, kind: YoutubeKind, index: int):
    from YouTube.youtube_downloader import get_streams_by_format

    if index < 1:
        raise ValidationError("Stream index must be at least 1.")
    kind_str = (
        "audio"
        if kind == YoutubeKind.AUDIO
        else ("audio+video" if kind == YoutubeKind.AUDIO_VIDEO else "video")
    )
    streams = list(get_streams_by_format(yt, kind_str))
    stream_list = streams
    if index > len(stream_list):
        raise ValidationError("Selected stream does not exist.")
    return stream_list[index - 1]


def get_stream_by_itag(yt: pyt.YouTube, kind: YoutubeKind, itag: int):
    """Return the stream with this itag among the streams of ``kind``.

    Safer than an index: YouTube may return a different stream list between
    the analysis and the download.
    """
    from YouTube.youtube_downloader import get_streams_by_format

    for stream in get_streams_by_format(yt, kind_to_label(kind)):
        if getattr(stream, "itag", None) == itag:
            return stream
    raise ValidationError("The selected stream is no longer offered by YouTube. Analyze the URL again.")


def download_stream(
    yt: pyt.YouTube,
    stream,
    yt_title: str,
    output_dir: str,
    filename_stem: str | None,
    cancel_event=None,
    on_progress: Callable[[float | None, str], None] | None = None,
) -> str:
    """Download stream; returns final file path. Raises DownloadError on failure."""

    def _progress_hook(stream_obj, _chunk: bytes, bytes_remaining: int) -> None:
        if on_progress is None:
            return
        total = getattr(stream_obj, "filesize", None) or getattr(stream_obj, "filesize_approx", None)
        if total and int(total) > 0:
            done = int(total) - int(bytes_remaining)
            on_progress(max(0.0, min(1.0, done / int(total))), "Downloading…")
        else:
            on_progress(None, "Downloading…")

    base_name = func.sanitize_filename(filename_stem if filename_stem else yt_title)

    def _interrupt() -> bool:
        return bool(cancel_event is not None and cancel_event.is_set())

    previous_progress = yt.stream_monostate.on_progress
    try:
        if on_progress:
            yt.register_on_progress_callback(_progress_hook)
        from YouTube.youtube_downloader import download_stream_to

        final_path = download_stream_to(
            stream,
            output_dir,
            base_name,
            interrupt_checker=_interrupt if cancel_event is not None else None,
        )
        if final_path is None:
            raise DownloadError("Download was interrupted before it finished.")
        if on_progress:
            on_progress(1.0, f"Saved: {final_path}")
        return final_path
    except Exception as exc:
        if cancel_event is not None and cancel_event.is_set():
            raise DownloadError("Download cancelled.") from exc
        raise DownloadError(f"Download failed: {exc}") from exc
    finally:
        yt.stream_monostate.on_progress = previous_progress
