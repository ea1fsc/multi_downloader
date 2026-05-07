# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Desktop GUI (`desktop_main.py`) built with PySide6: download tab with analyze/stream selection, progress log, SQLite history, JSON settings, background downloads via thread pool.
- Application layer under `app/` (domain models, `DownloadService`, settings/history persistence via `platformdirs`).
- Non-interactive adapters for YouTube/Twitter/Instagram used by the GUI (`app/adapters/`).
- Optional dependencies `[gui]` / `requirements-gui.txt`; console script `multi-downloader-gui`.
- Tests for download service and history store (`tests/test_download_service.py`).

### Changed
- `common/functions.check_url_accessibility` accepts `quiet=True` for GUI-friendly checks without printing.
- `pyproject.toml`: setuptools packages include `app`/`ui`, optional GUI deps, entry point for the GUI.

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
