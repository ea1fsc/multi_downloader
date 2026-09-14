"""Build a standalone multi-downloader binary (CLI and GUI) with PyInstaller."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIST = ROOT / "dist"
DEFAULT_WORK = ROOT / "build" / "pyinstaller"
HIDDEN_IMPORTS = [
    "ui",
    "ui.main_window",
    "ui.workers",
    "app",
    "app.adapters",
    "app.adapters.instagram_adapter",
    "app.adapters.twitter_adapter",
    "app.adapters.youtube_adapter",
    "app.domain",
    "app.domain.errors",
    "app.domain.models",
    "app.services",
    "app.services.download_service",
    "app.services.history_service",
    "app.services.settings_service",
    "Instagram",
    "Instagram.instagram_downloader",
    "Twitter",
    "Twitter.twitter_downloader",
    "YouTube",
    "YouTube.youtube_downloader",
    "common",
    "common.functions",
    "common.variables",
    "common.check_libraries",
    "platformdirs",
]
COLLECT_ALL = ("PySide6", "pytubefix", "yt_dlp", "instaloader")


def build(distpath: Path, workpath: Path) -> int:
    try:
        import PyInstaller.__main__
    except ImportError:
        print(
            "PyInstaller is not installed.\n"
            "Install it with: pip install pyinstaller",
            file=sys.stderr,
        )
        return 1

    distpath.mkdir(parents=True, exist_ok=True)
    workpath.mkdir(parents=True, exist_ok=True)
    specpath = workpath / "spec"
    specpath.mkdir(parents=True, exist_ok=True)

    args = [
        str(ROOT / "multi_downloader.py"),
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "multi-downloader",
        "--console",
        "--paths",
        str(ROOT),
        "--distpath",
        str(distpath),
        "--workpath",
        str(workpath),
        "--specpath",
        str(specpath),
    ]
    for package in COLLECT_ALL:
        args.extend(["--collect-all", package])
    for hidden in HIDDEN_IMPORTS:
        args.extend(["--hidden-import", hidden])

    PyInstaller.__main__.run(args)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the multi-downloader binary.")
    parser.add_argument(
        "--dist",
        type=Path,
        default=DEFAULT_DIST,
        help="Output directory for the binary (default: dist/).",
    )
    parser.add_argument(
        "--work",
        type=Path,
        default=DEFAULT_WORK,
        help="PyInstaller work directory (default: build/pyinstaller/).",
    )
    args = parser.parse_args(argv)
    return build(args.dist.resolve(), args.work.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
