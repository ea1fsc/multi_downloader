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


def test_parse_args_gui_long_and_short() -> None:
    assert md.parse_args(["--gui"]).gui is True
    assert md.parse_args(["-g"]).gui is True
    assert md.parse_args([]).gui is False
    assert md.parse_args(["--platform", "youtube"]).gui is False


def test_main_gui_flag_skips_cli(monkeypatch) -> None:
    monkeypatch.setattr(md, "launch_gui", lambda: 0)
    monkeypatch.setattr(md, "run_interactive_menu", lambda: 99)
    monkeypatch.setattr(md, "run_non_interactive", lambda _args: 98)
    assert md.main(["--gui"]) == 0
    assert md.main(["-g", "--platform", "youtube"]) == 0


def test_launch_gui_missing_pyside(monkeypatch, capsys) -> None:
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "PySide6" or name.startswith("PySide6."):
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    assert md.launch_gui() == 1
    err = capsys.readouterr().err
    assert "GUI dependencies" in err
    assert "requirements.txt" in err
