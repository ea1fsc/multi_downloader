# Getting started

`multi_downloader` is a local Python app (terminal menu, CLI flags, or optional desktop GUI). It does not log into your social accounts by default, and it does not run as a background service.

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
- are fine with a terminal menu, a few CLI flags, or the optional Qt GUI (`--gui`).

Do **not** expect private-account login or playlist/profile dumps. See [Limitations](limitations.md).

## Typical first run

1. Follow [Installation](installation.md) (venv + `pip install -r requirements.txt`).
2. Optionally run `python common/check_libraries.py`.
3. Start the menu: `python multi_downloader.py`. For the desktop UI, install GUI extras and run `python multi_downloader.py --gui`.
4. Choose a platform, paste a full post URL, confirm, pick a folder (Enter = default Downloads), set a filename (Enter = default).

Non-interactive flags are documented in [Usage](usage.md). URL formats: [Platforms](platforms.md). A standalone binary is documented in [Building](building.md).

## Next step

- Ready to install? [Installation](installation.md).
- Already installed? [Usage](usage.md).
- Want a standalone binary? [Building](building.md).
- Download failed? [Troubleshooting](troubleshooting.md).
