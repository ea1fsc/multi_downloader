# Limitations

Facts about the current tree (CLI plus optional GUI). Feature requests: GitHub issues.

## Accounts and private content

- No login flow in this repo. Instagram uses anonymous Instaloader. Private posts, age-gated YouTube, and logged-in-only tweets are out of scope.
- Instagram stories, highlights, profiles, and multi-image carousels (as separate files) are not implemented.
- Twitter/X **text-only** posts have no downloadable media and are rejected.

## CLI

- `--yes` does not skip filename prompts.
- `--output` must be an existing directory; the program will not create it.
- Non-interactive mode still needs stdin for those filename prompts unless you feed a newline.

## YouTube quality

Progressive (`audio+video`) streams are usually only **360p** today, and only some pytubefix clients can download them. Higher resolutions are video-only (`--mode video`) with no audio mux in this project.

## Desktop UI

- `python multi_downloader.py --gui` prints an install hint if PySide6 is missing (`pip install -r requirements.txt`).
- Analyze runs on the UI thread and can freeze the window until metadata returns.
- Instagram cancel only applies before the transfer starts. `collision_policy` in settings is stored but not applied yet.
- Closing the window during a download asks for confirmation and cancels it. The app still waits for the transfer to stop, so an Instagram download that already started runs to completion first.
- Changing the URL or the YouTube mode discards the last analysis; analyze again before downloading.
- Twitter/X posts with several videos are untested and may be rejected as having no downloadable media.
- The GUI adapters are a second download path; behaviour can drift from the CLI modules.

## Version metadata

Git tags and the root `CHANGELOG.md` go through **v0.4**. `pyproject.toml` lists `version = "0.4.0"`.

## Legal

You are responsible for what you download and for each site’s terms of use. This software is a local helper, not a circumvention service we operate.

## Maintenance

One maintainer. Platform libraries (`instaloader`, `yt-dlp`, `pytubefix`) break when sites change. Expect retries and dependency upgrades more often than new features.
