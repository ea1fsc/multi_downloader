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


class _ItagStream:
    def __init__(self, itag: int, abr: str) -> None:
        self.itag = itag
        self.abr = abr


class _ItagQuery(list):
    def filter(self, **_kwargs):
        return self


class _ItagYoutube:
    def __init__(self, streams) -> None:
        self.streams = _ItagQuery(streams)


def test_get_stream_by_itag_ignores_list_order() -> None:
    from app.adapters import youtube_adapter as yt_ad

    wanted = _ItagStream(251, "160kbps")
    yt = _ItagYoutube([_ItagStream(140, "128kbps"), wanted, _ItagStream(139, "48kbps")])
    assert yt_ad.get_stream_by_itag(yt, YoutubeKind.AUDIO, 251) is wanted


def test_get_stream_by_itag_missing_raises() -> None:
    from app.adapters import youtube_adapter as yt_ad

    yt = _ItagYoutube([_ItagStream(140, "128kbps")])
    with pytest.raises(ValidationError):
        yt_ad.get_stream_by_itag(yt, YoutubeKind.AUDIO, 251)


def test_execute_youtube_prefers_itag(monkeypatch, tmp_path) -> None:
    from app.services import download_service as ds

    calls: list = []
    monkeypatch.setattr(ds.yt_ad, "load_video", lambda _url, kind=None: type("Yt", (), {"title": "t"})())
    monkeypatch.setattr(ds.yt_ad, "get_stream_by_itag", lambda _yt, _kind, itag: calls.append(("itag", itag)))
    monkeypatch.setattr(ds.yt_ad, "get_stream_by_index", lambda _yt, _kind, idx: calls.append(("index", idx)))
    monkeypatch.setattr(ds.yt_ad, "download_stream", lambda *a, **k: str(tmp_path / "t.webm"))
    job = DownloadJob(
        platform=Platform.YOUTUBE,
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir=str(tmp_path),
        youtube_kind=YoutubeKind.AUDIO,
        youtube_stream_index=1,
        youtube_itag=251,
    )
    outcome = DownloadService().execute(job, threading.Event())
    assert outcome.success
    assert calls == [("itag", 251)]


def test_history_service_closes_connections(tmp_path) -> None:
    import sqlite3

    from app.services.history_service import HistoryService

    svc = HistoryService(db_path=tmp_path)
    with svc._connect() as conn:
        conn.execute("SELECT 1")
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")


def test_analyze_youtube_surfaces_stream_errors(monkeypatch) -> None:
    from app.domain.errors import DownloadError
    from app.services import download_service as ds

    def boom(_yt, _kind):
        raise RuntimeError("detected as a bot")

    monkeypatch.setattr(ds.func, "check_url_accessibility", lambda *_a, **_k: True)
    monkeypatch.setattr(ds.yt_ad, "load_video", lambda _url, kind=None: type("Yt", (), {"title": "t"})())
    monkeypatch.setattr(ds.yt_ad, "preview_dict", lambda _yt: {})
    monkeypatch.setattr(ds.yt_ad, "list_streams_for_kind", boom)
    with pytest.raises(DownloadError, match="detected as a bot"):
        DownloadService().analyze(Platform.YOUTUBE, "https://youtu.be/dQw4w9WgXcQ", youtube_kind=YoutubeKind.AUDIO)


def test_twitter_fetch_info_surfaces_reason(monkeypatch) -> None:
    from app.adapters import twitter_adapter as tw_ad
    from app.domain.errors import DownloadError

    class FailingYDL:
        def __init__(self, _opts):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def extract_info(self, _url, download=False):
            raise RuntimeError("login required")

    monkeypatch.setattr(tw_ad.yt_dlp, "YoutubeDL", FailingYDL)
    with pytest.raises(DownloadError, match="login required"):
        tw_ad.fetch_info("https://x.com/u/status/1")


def test_execute_youtube_loads_video_with_job_kind(monkeypatch, tmp_path) -> None:
    from app.services import download_service as ds

    kinds: list = []

    def fake_load(_url, kind=None):
        kinds.append(kind)
        return type("Yt", (), {"title": "t"})()

    monkeypatch.setattr(ds.yt_ad, "load_video", fake_load)
    monkeypatch.setattr(ds.yt_ad, "get_stream_by_itag", lambda *_a: object())
    monkeypatch.setattr(ds.yt_ad, "download_stream", lambda *a, **k: str(tmp_path / "t.mp4"))
    job = DownloadJob(
        platform=Platform.YOUTUBE,
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir=str(tmp_path),
        youtube_kind=YoutubeKind.AUDIO_VIDEO,
        youtube_itag=18,
    )
    assert DownloadService().execute(job, threading.Event()).success
    assert kinds == [YoutubeKind.AUDIO_VIDEO]
