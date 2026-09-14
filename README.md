# multi_downloader

Local downloader for **Instagram**, **Twitter/X**, and **YouTube**. Run it from a terminal menu, with CLI flags, or with an optional **desktop GUI**. There is no server and no account of ours to configure. Current tagged release: **v0.3**. License **GPL-3.0**.

## Documentation

Guides (English) live in [`docs/`](docs/):

| Guide | Audience |
| --- | --- |
| [Getting started](docs/getting-started.md) | Anyone new to the project |
| [Installation](docs/installation.md) · [Configuration](docs/configuration.md) | Person who runs it on their computer |
| [Usage](docs/usage.md) · [Platforms](docs/platforms.md) | People downloading media |
| [Building](docs/building.md) | Standalone binary and OS packages |
| [How it works](docs/how-it-works.md) · [Limitations](docs/limitations.md) | Operators and reviewers |
| [Troubleshooting](docs/troubleshooting.md) | When a download fails |
| [Development](docs/development.md) | Contributors |

This README is a short overview. Prefer the docs folder if you are installing or using the tool for the first time.

## What it does

1. You pick a platform (menu, `--platform`, or the GUI).
2. You pass a **post or video URL** (not a profile).
3. The tool fetches metadata with the platform library (`instaloader`, `yt-dlp`, or `pytubefix`), asks you to confirm when it can, then writes a file to a directory you choose.

Interactive menu:

```bash
python multi_downloader.py
```

Desktop GUI:

```bash
python multi_downloader.py --gui
```

One-shot (YouTube audio example; the output directory must already exist):

```bash
python multi_downloader.py --platform youtube --url "https://youtu.be/dQw4w9WgXcQ" --mode audio --output "/tmp" --yes
```

`--yes` skips confirmations. Filename prompts still appear; press Enter to keep the default name. Details: [Usage](docs/usage.md).

## Prerequisites

- Python **3.12 or newer** (see `.python-version`)
- Network access to Instagram, Twitter/X, and/or YouTube
- A writable download directory (default: `Descargas` or `Downloads` under your home folder)

Install: [Installation](docs/installation.md) (`pip install -r requirements.txt` covers CLI and GUI). There is no `.env` file; flags, prompts, and (in the GUI) a local settings file are the configuration. See [Configuration](docs/configuration.md).

Standalone binaries and Linux packages: [Building](docs/building.md). GitHub tags matching `vX`, `vX.Y`, or `vX.Y.Z` publish a release with those artifacts.

## Project layout

```
multi_downloader.py          # Menu, CLI dispatcher, and --gui launcher
app/                         # GUI application layer (adapters, services)
ui/                          # PySide6 window and background workers
Instagram/                   # Instaloader-based post downloader
Twitter/                     # yt-dlp tweet video downloader
YouTube/                     # pytubefix stream picker
common/                      # Shared prompts, URL check, filenames
packaging/                   # PyInstaller build and Linux package helpers
tests/                       # pytest (no live downloads)
```

## Changelog

Release history: [CHANGELOG.md](CHANGELOG.md).
