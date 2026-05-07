"""Domain models and DTOs shared by CLI adapters (future) and the desktop UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    YOUTUBE = "youtube"


class YoutubeKind(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
    AUDIO_VIDEO = "audio+video"


class ProgressStage(str, Enum):
    QUEUED = "queued"
    PREPARING = "preparing"
    DOWNLOADING = "downloading"
    POSTPROCESSING = "postprocessing"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ProgressEvent:
    stage: ProgressStage
    message: str = ""
    fraction: float | None = None  # 0.0–1.0 when known


@dataclass
class StreamOption:
    """YouTube stream choice presented to the user (1-based index matches CLI)."""

    index: int
    label: str
    kind: YoutubeKind


@dataclass
class MediaInfo:
    """Result of analyzing a URL before download."""

    platform: Platform
    url: str
    title: str | None = None
    subtitle: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
    youtube_streams: list[StreamOption] = field(default_factory=list)
    suggested_filename_stem: str | None = None


@dataclass
class DownloadJob:
    """Parameters required to execute a download."""

    platform: Platform
    url: str
    output_dir: str
    assume_confirm: bool = True
    filename_stem: str | None = None
    youtube_kind: YoutubeKind | None = None
    youtube_stream_index: int | None = None  # 1-based


@dataclass
class DownloadOutcome:
    success: bool
    output_path: str | None = None
    message: str | None = None


@dataclass
class AppSettings:
    schema_version: int = 1
    default_download_dir: str | None = None
    collision_policy: str = "rename"  # rename | overwrite (best-effort per platform)


@dataclass
class HistoryEntry:
    id: int | None
    created_at: datetime
    platform: Platform
    url: str
    title: str | None
    output_path: str | None
    status: str
    error_message: str | None = None


@dataclass
class HistoryFilter:
    limit: int = 100
    offset: int = 0
