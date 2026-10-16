# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Security
- Linux packages installed `/usr/bin/multi-downloader` owned by the build user (e.g. uid 1001 on CI) instead of root, letting that uid replace a binary on everyone's `PATH`. The `.deb` is now built with `dpkg-deb --root-owner-group` and the Arch package stores `root:root` ownership.
- The release workflow granted `contents: write` to every job, including builds that install unpinned third-party packages. Write access is now limited to the `release` job.

### Added
- CI workflow (`.github/workflows/tests.yml`) runs the test suite on every branch push and pull request; the release workflow runs it first and builds nothing if it fails.

### Changed
- Linux packages declare the desktop GUI's system libraries: `Recommends` in the `.deb` (installed by default by `apt install ./file.deb`) and `optdepends` in the Arch packages, so `--gui` works on minimal installs while terminal-only systems can skip them.
- The release build installs the xcb-util, xkbcommon-x11 and fontconfig libraries so PyInstaller bundles them into the Linux binary.
- YouTube streams are listed best quality first (audio by bitrate, video by resolution then fps), so `--yes` and the GUI default pick the best stream instead of the first one returned by YouTube.
- Require `pytubefix>=11.2`; older releases fail on current YouTube with bot detection or player parsing errors.
- GUI sorts YouTube streams by bitrate (audio) or resolution (video), descending, by default; a sort field picked by the user is kept across modes.
- GUI downloads select the YouTube stream by `itag` instead of its list position, so a different stream list at download time cannot pick another stream.
- `--url` must match the `--platform` URL format; otherwise the run exits with code `1` before any network request.
- One-shot runs (`--platform`) exit with `130` on Ctrl+C and with `1` and a clear message when stdin closes during a prompt. The interactive menu still exits with `0`.
- More URL forms accepted: YouTube `m.`, `music.` and `/live/`; Twitter/X `mobile.` and `/i/web/status/`.
- File names: control characters become spaces, trailing dots/spaces are removed, Windows reserved names get a `_` prefix, names are capped at 200 bytes, and a typed extension is not duplicated.
- Twitter/X downloads report the saved file path (CLI and GUI history) instead of the folder.

### Fixed
- Instagram downloads assumed `.jpg`/`.mp4`, but the file is saved with the extension of the server's `Content-Type` (e.g. `.webp`); the reported path and the name-collision check could be wrong. The extension is now taken from the response.
- Instagram reported "Download completed" when a file with the same name already existed and nothing was downloaded. A free name (`name_1`, …) is used instead.
- YouTube downloads cut short by an HTTP 404 (which pytubefix ignores) were reported as complete. The received size is now checked against the announced size.
- GUI rendered titles, captions, uploader names and error messages from the sites as HTML (links, local images, spoofed text). They are now shown as plain text.
- YouTube downloads could destroy an unrelated file: pytubefix first wrote to `<video title>.<ext>` in the target folder, overwriting a file with that name, which was then renamed away. Downloads now go to a unique hidden temp file that is moved into place when complete and removed on cancel or error.
- YouTube audio-only WebM/Opus downloads were saved with a `.m4a` extension (pytubefix names every audio stream `.m4a`); the extension now follows the stream's MIME type in both CLI and GUI.
- GUI kept the previous video's file name after analyzing a new URL, which could overwrite the earlier download.
- GUI could download using a previous analysis after the URL or YouTube mode changed; changing either now discards the analysis.
- GUI history recorded the title of whatever was analyzed when a download finished instead of the one downloaded.
- Closing the GUI during a download now asks for confirmation and cancels the download.
- Download history no longer leaves SQLite connections open.
- GUI shows the real error when YouTube streams or Twitter/X metadata cannot be fetched, instead of "no streams" or a generic message.
- `%` in Twitter/X file names is no longer expanded as a yt-dlp template field.
- YouTube `audio+video` (progressive) mode found no streams with pytubefix 11, whose default client lists none. It now retries with clients that offer a downloadable progressive stream, and analysis and download use the same client.
- Listing YouTube streams no longer crashes when the size lookup fails (e.g. HTTP 403); the size shows as `N/A`.

## [v0.4] - 2026-09-14

### Added
- Desktop GUI built with PySide6: download tab with analyze/stream selection, progress log, SQLite history, JSON settings, background downloads via thread pool.
- Application layer under `app/` (domain models, `DownloadService`, settings/history persistence via `platformdirs`).
- Non-interactive adapters for YouTube/Twitter/X/Instagram used by the GUI (`app/adapters/`).
- Unified console script `multi-downloader`.
- `--gui` / `-g` on `multi_downloader.py` to launch the desktop UI from the same entry point as the CLI.
- Tests for download service and history store (`tests/test_download_service.py`).
- Standalone binary build (`packaging/build.py`) and Linux `.deb` / Arch `pkg.tar.xz` helpers.
- GitHub Actions release workflow on tags `vX`, `vX.Y`, or `vX.Y.Z` (Windows, macOS, and Linux artifacts plus source).
- Building guide (`docs/building.md`).

### Changed
- `common/functions.check_url_accessibility` accepts `quiet=True` for GUI-friendly checks without printing.
- `pyproject.toml`: setuptools packages include `app`/`ui`, runtime GUI libraries, single `multi-downloader` entry point.
- `requirements.txt` installs every runtime library for CLI and GUI (`PySide6`, `platformdirs` included); `requirements-gui.txt` and the `[gui]` extra were removed.
- Documentation covers the GUI, a single dependency file, compilation, and tagged releases.

### Fixed
- YouTube CLI preview used an undefined `separator` variable in `YouTube/youtube_downloader.py`.

## [v0.3] - 2026-05-07

### Added
- Twitter/X downloader module.
- Non-interactive CLI execution mode in `multi_downloader.py`.
- Automated tests for helpers and URL validation flows.
- Pytest configuration via `pytest.ini`.

### Changed
- Codebase refactor and downloader flow unification.
- Downloader banners and CLI UX refresh.
- Prompt handling now accepts `y/yes/n/no`.
- Instagram shortcode extraction improved for `post`, `reel`, and `tv` URL formats.
- README expanded with installation, testing, and troubleshooting updates.
- Project language standardized to English.

### Fixed
- Redownload flow when switching to a different URL.
- Instagram `403` handling improvements and clearer user-facing error messaging.

## [v0.2] - 2024-09-26

### Added
- Instagram downloader support.
- Ability to download Instagram post photos, videos, and reels from public URLs.

## [v0.1] - 2024-08-30

### Added
- Initial repository setup and `.gitignore`.
