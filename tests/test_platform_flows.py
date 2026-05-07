"""Behavior tests for platform downloader flows."""

from __future__ import annotations

from Instagram import instagram_downloader as ig
from Twitter import twitter_downloader as tw
from YouTube import youtube_downloader as yt


def test_instagram_main_success_exit(monkeypatch):
    monkeypatch.setattr(ig, "get_instagram_url", lambda: "https://www.instagram.com/p/ABC123DEF45/")
    monkeypatch.setattr(ig.func, "check_url_accessibility", lambda _url: True)
    monkeypatch.setattr(ig, "download_instagram_post", lambda _url, output_dir=None: True)
    monkeypatch.setattr(ig.func, "ask_yes_no", lambda _prompt: False)
    assert ig.main() == 0


def test_twitter_main_returns_zero_after_download(monkeypatch):
    monkeypatch.setattr(tw, "request_twitter_url", lambda: "https://x.com/user/status/1234567890")
    monkeypatch.setattr(tw.func, "check_url_accessibility", lambda _url: True)
    monkeypatch.setattr(tw, "get_tweet_info", lambda _url: {"ext": "mp4", "title": "a", "formats": [1]})
    monkeypatch.setattr(tw, "confirm_tweet", lambda _info: True)
    monkeypatch.setattr(
        tw,
        "download_tweet_video",
        lambda _url, _info, output_dir=None: (True, "/tmp"),
    )
    monkeypatch.setattr(tw, "ask_download_another", lambda: False)
    assert tw.main() == 0


def test_youtube_main_returns_zero_when_user_stops(monkeypatch):
    class FakeYt:
        title = "video-title"

    monkeypatch.setattr(yt, "request_url", lambda: "https://youtu.be/dQw4w9WgXcQ")
    monkeypatch.setattr(yt.func, "check_url_accessibility", lambda _url: True)
    monkeypatch.setattr(yt, "build_and_confirm_yt", lambda _url, assume_yes=False: (True, FakeYt()))
    monkeypatch.setattr(yt, "ask_mode", lambda: "audio")
    monkeypatch.setattr(yt, "get_streams_by_format", lambda _yt, _kind: ["stream"])
    monkeypatch.setattr(yt, "choose_stream", lambda _streams, _label, auto_select=False: "stream")
    monkeypatch.setattr(yt, "download_stream", lambda _stream, _title, output_dir=None: True)
    monkeypatch.setattr(yt, "ask_another_and_same_url", lambda: (False, False))
    assert yt.main() == 0
