"""Tests for application-layer download service (no GUI imports)."""

from __future__ import annotations

import threading

import pytest

from app.domain.errors import ValidationError
from app.domain.models import DownloadJob, Platform, ProgressStage, YoutubeKind
from app.services.download_service import DownloadService


def test_analyze_youtube_invalid_url() -> None:
    svc = DownloadService()
    with pytest.raises(ValidationError):
        svc.analyze(Platform.YOUTUBE, "not-a-url", youtube_kind=YoutubeKind.AUDIO)


def test_execute_youtube_missing_stream() -> None:
    svc = DownloadService()
    job = DownloadJob(
        platform=Platform.YOUTUBE,
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir="/tmp",
        youtube_kind=None,
        youtube_stream_index=None,
    )
    cancel = threading.Event()
    events: list = []

    def on_prog(ev) -> None:
        events.append(ev)

    out = svc.execute(job, cancel, on_prog)
    assert out.success is False
    assert "requires stream" in (out.message or "").lower()


def test_execute_emits_preparing() -> None:
    svc = DownloadService()
    job = DownloadJob(
        platform=Platform.YOUTUBE,
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir="/tmp",
        youtube_kind=None,
        youtube_stream_index=None,
    )
    cancel = threading.Event()
    stages: list = []

    def on_prog(ev) -> None:
        stages.append(ev.stage)

    svc.execute(job, cancel, on_prog)
    assert ProgressStage.PREPARING in stages


def test_history_service_roundtrip(tmp_path) -> None:
    from app.services.history_service import HistoryService

    h = HistoryService(db_path=tmp_path)
    hid = h.add_entry(
        platform=Platform.TWITTER,
        url="https://x.com/u/status/1",
        title="t",
        output_path="/tmp/x",
        status="success",
    )
    assert hid >= 1
    rows = h.list_entries()
    assert len(rows) == 1
    assert rows[0].platform == Platform.TWITTER


def test_history_service_accepts_platform_string(tmp_path) -> None:
    from app.services.history_service import HistoryService

    h = HistoryService(db_path=tmp_path)
    hid = h.add_entry(
        platform="youtube",
        url="https://youtu.be/dQw4w9WgXcQ",
        title="yt",
        output_path="/tmp/y",
        status="success",
    )
    assert hid >= 1
    rows = h.list_entries()
    assert len(rows) == 1
    assert rows[0].platform == Platform.YOUTUBE


def test_history_service_clear(tmp_path) -> None:
    from app.services.history_service import HistoryService

    h = HistoryService(db_path=tmp_path)
    h.add_entry(
        platform=Platform.INSTAGRAM,
        url="https://instagram.com/p/abc/",
        title="ig",
        output_path="/tmp/i",
        status="success",
    )
    assert len(h.list_entries()) == 1
    h.clear()
    assert h.list_entries() == []
