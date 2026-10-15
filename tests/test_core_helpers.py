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


def test_extract_shortcode_from_instagram_reel_url_with_query_params() -> None:
    assert (
        extract_shortcode("https://www.instagram.com/reel/DX9WQm5tUd0/?utm_source=ig_web_copy_link")
        == "DX9WQm5tUd0"
    )


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


def test_ask_yes_no_accepts_full_yes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "yes")
    assert func.ask_yes_no("Continue? ") is True


def test_ask_yes_no_accepts_full_no(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "no")
    assert func.ask_yes_no("Continue? ") is False


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


def test_sanitize_filename_replaces_control_chars() -> None:
    assert func.sanitize_filename("line1\nline2\tend") == "line1 line2 end"


def test_sanitize_filename_strips_trailing_dots_and_spaces() -> None:
    assert func.sanitize_filename("title... ") == "title"


def test_sanitize_filename_avoids_windows_reserved_names() -> None:
    assert func.sanitize_filename("CON") == "_CON"
    assert func.sanitize_filename("nul.txt") == "_nul.txt"
    assert func.sanitize_filename("Console") == "Console"


def test_sanitize_filename_limits_utf8_length() -> None:
    result = func.sanitize_filename("é" * 300)
    assert len(result.encode("utf-8")) <= func.MAX_FILENAME_BYTES
    assert result == "é" * (func.MAX_FILENAME_BYTES // 2)


def test_strip_extension_only_removes_matching_extension() -> None:
    assert func.strip_extension("photo.JPG", ".jpg") == "photo"
    assert func.strip_extension("song.m4a", ".webm") == "song.m4a"
    assert func.strip_extension(".jpg", ".jpg") == ".jpg"


def test_build_target_stem_does_not_duplicate_extension(tmp_path: Path) -> None:
    stem = build_target_stem(str(tmp_path), "holiday.jpg", "ABC", ".jpg")
    assert stem == str(tmp_path / "holiday")


@pytest.mark.parametrize(
    "url",
    [
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/live/dQw4w9WgXcQ",
    ],
)
def test_youtube_url_validator_accepts_more_hosts(url: str) -> None:
    from YouTube.youtube_downloader import is_valid_youtube_url

    assert is_valid_youtube_url(url)


@pytest.mark.parametrize(
    "url",
    ["https://x.com/i/web/status/1234567890", "https://mobile.twitter.com/user/status/1234567890"],
)
def test_twitter_url_validator_accepts_web_and_mobile(url: str) -> None:
    from Twitter.twitter_downloader import is_valid_twitter_url

    assert is_valid_twitter_url(url)


def test_twitter_output_template_escapes_percent_and_mp4(tmp_path: Path) -> None:
    from Twitter.twitter_downloader import build_output_template

    assert build_output_template(tmp_path, "100% a %(id)s") == str(tmp_path / "100%% a %%(id)s.%(ext)s")
    assert build_output_template(tmp_path, "clip.mp4") == str(tmp_path / "clip.%(ext)s")
