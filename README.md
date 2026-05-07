# multi_downloader

A multi-platform media downloader for Instagram, Twitter/X, and YouTube that runs locally from your terminal or via an optional **desktop GUI** (Qt/PySide6).

## Disclaimer

This project is maintained by one person, so feature delivery may be gradual. Feedback, bug reports, and contributions are very welcome.

## Features

- **Instagram Downloader:** downloads post media (image/video), lets you choose destination folder, and supports custom filenames.
- **Twitter/X Downloader:** downloads video posts using `yt-dlp`, with post preview/confirmation and custom output naming.
- **YouTube Downloader:** supports audio-only, video-only, or progressive audio+video download modes with stream selection.

## Installation

1. Create and activate a virtual environment.
2. Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

For the desktop UI, also install GUI dependencies:

```bash
pip install -r requirements-gui.txt
```

(or `pip install -e ".[gui]"` / `pip install -e ".[dev]"` — see `pyproject.toml`.)

Alternative (editable install with metadata in `pyproject.toml`):

```bash
pip install -e .
```

3. Optionally verify dependencies:

```bash
python common/check_libraries.py
```

## Quickstart

Run the main menu:

```bash
python multi_downloader.py
```

Run the **desktop application**:

```bash
python desktop_main.py
```

After editable install, you can also use:

```bash
multi-downloader-gui
```

Run non-interactive mode (single platform):

```bash
python multi_downloader.py --platform youtube --url "https://youtu.be/dQw4w9WgXcQ" --mode audio --output "/tmp" --yes
```

Run a single module directly:

```bash
python Instagram/instagram_downloader.py
python Twitter/twitter_downloader.py
python YouTube/youtube_downloader.py
```

## Testing

This project uses `pytest`.

Run all tests:

```bash
pytest
```

Current tests focus on:
- shared helpers in `common/functions.py`
- URL validation flows for Instagram/Twitter/X/YouTube
- Instagram helper logic for shortcode extraction and output naming collisions

## Project structure

- `multi_downloader.py`: main menu/orchestrator.
- `desktop_main.py`: Qt desktop UI entry point.
- `app/`: application layer (domain models, services, platform adapters for the GUI).
- `ui/`: PySide6 widgets and background workers.
- `common/`: shared helpers and shared constants.
- `Instagram/`, `Twitter/`, `YouTube/`: platform-specific download modules.
- `tests/`: automated test suite.

## Current limitations

- Some platform behaviors depend on external services/libraries and can change over time.
- Private-account login flows are not fully implemented.
- The GUI shares the same download engines as the CLI; long-running work runs in a background thread pool.

## Packaging the GUI (optional)

To produce a standalone binary (example with PyInstaller, from the repo root with GUI deps installed):

```bash
pyinstaller --onefile --windowed --name multi-downloader-gui desktop_main.py
```

You may need extra `--hidden-import` flags for `PySide6` submodules depending on your environment.

## Troubleshooting

- If dependency checks fail, run `pip install -r requirements.txt` again in the active virtual environment.
- If a URL is rejected, verify the full post/video URL format (not a profile or short share link without an ID).
- If a download fails unexpectedly, retry later (platform APIs and scraping endpoints may be temporarily unstable).
- Instagram may return intermittent `graphql/query` `403` responses when anonymous metadata requests are rate-limited. In that case:
  - retry after a few minutes,
  - reduce request bursts,
  - or use an authenticated `instaloader` session/cookies to improve reliability.

## Changelog

Project history is tracked in `CHANGELOG.md`.