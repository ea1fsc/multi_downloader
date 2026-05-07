"""Tests for top-level non-interactive CLI dispatcher."""

from __future__ import annotations

import argparse

import multi_downloader as md


def test_run_non_interactive_instagram_dispatch(monkeypatch):
    monkeypatch.setattr(md.os.path, "isdir", lambda _path: True)
    monkeypatch.setattr(md.ind, "main", lambda **kwargs: 0)
    args = argparse.Namespace(
        platform="instagram",
        url="https://www.instagram.com/p/ABC123DEF45/",
        output="/tmp",
        yes=True,
        mode=None,
    )
    assert md.run_non_interactive(args) == 0


def test_run_non_interactive_invalid_output_returns_error(monkeypatch):
    monkeypatch.setattr(md.os.path, "isdir", lambda _path: False)
    args = argparse.Namespace(
        platform="youtube",
        url="https://youtu.be/dQw4w9WgXcQ",
        output="/invalid",
        yes=True,
        mode="audio",
    )
    assert md.run_non_interactive(args) == 1
