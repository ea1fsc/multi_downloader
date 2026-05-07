# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Pytest configuration via `pytest.ini`.
- Expanded automated tests for:
  - shared helpers in `common/functions.py`
  - dependency diagnostics in `common/check_libraries.py`
  - main flow behavior for Instagram, Twitter/X, and YouTube modules.
- Shared `tests/conftest.py` bootstrap to ensure project imports work reliably during test discovery.
- `pyproject.toml` with project metadata and optional `dev` dependency group.
- Non-interactive CLI mode in `multi_downloader.py` using:
  - `--platform`
  - `--url`
  - `--output`
  - `--yes`
  - `--mode` (YouTube)

### Changed
- Testing dependencies now include `pytest` in `requirements.txt`.
- README updated with installation, quickstart, testing, project structure, limitations, and troubleshooting sections.

## [0.1.0] - 2026-05-07

### Added
- Initial multi-platform CLI downloader with Instagram, Twitter/X, and YouTube modules.
- Common helper layer for URL checks, yes/no prompts, and download directory handling.
