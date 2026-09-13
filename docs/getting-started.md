# Getting started

`multi_downloader` is a local Python CLI. It does not log into your social accounts by default, and it does not run as a background service.

It wraps three libraries:

| Platform | Library | What you get |
| --- | --- | --- |
| Instagram | `instaloader` | Photo or video from a public `/p/`, `/reel/`, or `/tv/` URL |
| Twitter/X | `yt-dlp` | Video attached to a `…/status/<id>` post |
| YouTube | `pytubefix` | Audio, video-only, or progressive (muxed) stream |

You stay at the keyboard: confirm URLs, pick a stream on YouTube, and choose a filename.

## Who should use this

Use this project if you:

- want a small script you run yourself, not a hosted downloader;
- have **public** post or video URLs;
- are fine with a terminal menu or a few CLI flags.

Do **not** expect private-account login, playlist/profile dumps, or a GUI on `main`. See [Limitations](limitations.md).

## Typical first run

1. Follow [Installation](installation.md) (venv + `pip install -r requirements.txt`).
2. Optionally run `python common/check_libraries.py`.
3. Start the menu: `python multi_downloader.py`.
4. Choose `1` / `2` / `3`, paste a full post URL, confirm, pick a folder (Enter = default Downloads), set a filename (Enter = default).

Non-interactive flags are documented in [Usage](usage.md). URL formats: [Platforms](platforms.md).

## Next step

- Ready to install? [Installation](installation.md).
- Already installed? [Usage](usage.md).
- Download failed? [Troubleshooting](troubleshooting.md).
