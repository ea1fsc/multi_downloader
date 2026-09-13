# Limitations

Facts about the current `main` tree (v0.3 CLI). Feature requests: GitHub issues.

## Accounts and private content

- No login flow in this repo. Instagram uses anonymous Instaloader. Private posts, age-gated YouTube, and logged-in-only tweets are out of scope.
- Instagram stories, highlights, profiles, and multi-image carousels (as separate files) are not implemented.
- Twitter/X **text-only** posts have no downloadable media and are rejected.

## CLI

- `--yes` does not skip filename prompts.
- `--output` must be an existing directory; the program will not create it.
- Non-interactive mode still needs stdin for those filename prompts unless you feed a newline.
- YouTube interactive/one-shot metadata display currently raises `NameError` (`separator` is undefined). That blocks the YouTube path until the code is fixed.

## YouTube quality

Progressive (`audio+video`) streams from pytubefix are typically **720p or lower**. Higher resolutions are video-only (`--mode video`) with no audio mux in this project.

## Desktop UI

A PySide6 UI (`desktop_main.py`, `app/`, `ui/`) is on branch `feat/graphical-interface`. It is not released on `main`. Do not expect `python desktop_main.py` to work on this branch.

## Version metadata

Git tags and the root `CHANGELOG.md` go through v0.3. `pyproject.toml` still says `version = "0.1.0"`.

## Legal

You are responsible for what you download and for each site’s terms of use. This software is a local helper, not a circumvention service we operate.

## Maintenance

One maintainer. Platform libraries (`instaloader`, `yt-dlp`, `pytubefix`) break when sites change. Expect retries and dependency upgrades more often than new features.
