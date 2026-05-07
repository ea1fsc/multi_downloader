"""Pytest suite for core helpers and URL validators."""

from __future__ import annotations

from pathlib import Path

import pytest
import requests

from Instagram.instagram_downloader import build_target_stem, extract_shortcode, get_instagram_url
from Twitter.twitter_downloader import request_twitter_url
from YouTube.youtube_downloader import request_url
from common import functions as func


def test_sanitize_filename_replaces_invalid_chars() -> None:
    assert func.sanitize_filename('bad:/\\*?"<>|name') == "bad_name"


def test_extract_shortcode_from_instagram_url() -> None:
    assert extract_shortcode("https://www.instagram.com/p/CxYZ123abcD/") == "CxYZ123abcD"


def test_extract_shortcode_raises_on_empty_url_part() -> None:
    with pytest.raises(ValueError):
        extract_shortcode("/")


def test_build_target_stem_returns_unique_name(tmp_path: Path) -> None:
    existing_file = tmp_path / "sample.mp4"
    existing_file.write_text("x", encoding="utf-8")
    stem = build_target_stem(str(tmp_path), "sample", "fallback", ".mp4")
    assert stem.endswith("sample_1")


def test_ask_yes_no_retries_until_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = iter(["invalid", "Y"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert func.ask_yes_no("Continue? ") is True


def test_get_valid_download_directory_uses_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(func, "get_default_download_directory", lambda: str(tmp_path))
    selected = func.get_valid_download_directory(lambda _: "")
    assert selected == str(tmp_path)


def test_get_valid_download_directory_retries_when_invalid(tmp_path: Path) -> None:
    answers = iter(["/not-a-real-dir", str(tmp_path)])
    selected = func.get_valid_download_directory(lambda _: next(answers))
    assert selected == str(tmp_path)


def test_check_url_accessibility_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    class Response:
        status_code = 200

    monkeypatch.setattr(func.requests, "get", lambda *args, **kwargs: Response())
    assert func.check_url_accessibility("https://example.com") is True


def test_check_url_accessibility_request_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_error(*args, **kwargs):
        raise requests.RequestException("network error")

    monkeypatch.setattr(func.requests, "get", raise_error)
    assert func.check_url_accessibility("https://example.com") is False


def test_instagram_url_validator_retries_until_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = iter(["", "invalid", "https://www.instagram.com/p/ABC123DEF45/"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert get_instagram_url() == "https://www.instagram.com/p/ABC123DEF45/"


def test_twitter_url_validator_retries_until_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = iter(["https://example.com", "https://x.com/user/status/1234567890"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert request_twitter_url() == "https://x.com/user/status/1234567890"


def test_youtube_url_validator_retries_until_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = iter(["https://example.com", "https://youtu.be/dQw4w9WgXcQ"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert request_url() == "https://youtu.be/dQw4w9WgXcQ"
