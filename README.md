# multi_downloader

A multi-platform media downloader for Instagram, Twitter/X, and YouTube that runs locally from your terminal.

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

3. Optionally verify dependencies:

```bash
python common/check_libraries.py
```

## Quickstart

Run the main menu:

```bash
python multi_downloader.py
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
- `common/`: shared helpers and shared constants.
- `Instagram/`, `Twitter/`, `YouTube/`: platform-specific download modules.
- `tests/`: automated test suite.

## Current limitations

- Some platform behaviors depend on external services/libraries and can change over time.
- Private-account login flows are not fully implemented.
- The user flow is still CLI-interactive first (non-interactive CLI arguments are not implemented yet).

## Troubleshooting

- If dependency checks fail, run `pip install -r requirements.txt` again in the active virtual environment.
- If a URL is rejected, verify the full post/video URL format (not a profile or short share link without an ID).
- If a download fails unexpectedly, retry later (platform APIs and scraping endpoints may be temporarily unstable).