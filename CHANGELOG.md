# Changelog

All notable changes to this project will be documented in this file.

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
