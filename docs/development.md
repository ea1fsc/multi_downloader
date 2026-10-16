# Development

Audience: people changing this repository.

Language of the codebase, README, and docs is **English**. Issue templates live in `.github/ISSUE_TEMPLATE/` (`bug_report.md`, `feature_request.md`).

## Setup

Same as [Installation](installation.md) (`pip install -r requirements.txt` includes CLI and GUI libraries), then:

```bash
pip install -e ".[dev]"
pytest
```

`[dev]` is pytest only. You can skip it if you already installed `requirements.txt`, which lists pytest as well.

`pytest.ini`: `testpaths = tests`, `addopts = -q`, `pythonpath = .`. `tests/conftest.py` also inserts the repo root on `sys.path`.

| Test module | Covers |
| --- | --- |
| `test_core_helpers.py` | Filename sanitize and extension handling, Instagram shortcode/stems, yes/no, download dir, URL validators, Twitter output template |
| `test_platform_flows.py` | `main()` success paths with mocks (no live I/O); YouTube stream ordering, `--yes` auto-select, file extension and stem; `--url` validation; Twitter saved path |
| `test_cli_args.py` | `--platform` dispatcher, `--gui` / `-g`, invalid `--output`, exit codes for Ctrl+C and closed stdin |
| `test_check_libraries.py` | Import diagnostics |
| `test_download_service.py` | GUI download service (itag stream selection, error messages) and history store, including closed connections (no Qt window) |
| `test_main_window.py` | Desktop window state with offscreen Qt: analysis invalidation, auto-filled names, default stream sort, itag in jobs, close during download |
| `test_packaging_helpers.py` | CHANGELOG section extraction for releases |

Do not add tests that hit real Instagram/Twitter/YouTube.

GUI tests use Qt's offscreen platform (`QT_QPA_PLATFORM=offscreen`, set by `tests/test_main_window.py`), so they need no display, but PySide6 still loads system libraries: on Debian/Ubuntu install `libgl1 libegl1 libxkbcommon0 libfontconfig1 libdbus-1-3 libglib2.0-0` (as `.github/workflows/tests.yml` does).

## Layout

| Path | Role |
| --- | --- |
| `multi_downloader.py` | argparse, menu, and `--gui` launcher |
| `app/`, `ui/` | GUI services/adapters and PySide6 window |
| `Instagram/`, `Twitter/`, `YouTube/` | One package per site |
| `common/` | Shared CLI helpers |
| `packaging/` | PyInstaller build and Linux package helpers |
| `tests/` | pytest |
| `docs/` | These guides (published to the wiki; see below) |
| `.github/workflows/tests.yml` | `pytest` on every branch push and pull request (Ubuntu, Python 3.12, offscreen Qt); also run by `release.yml` before building |
| `.github/workflows/release.yml` | Tagged-release binaries and packages |

Standalone builds: [Building](building.md).

## Conventions

- Platform `main(..., preset_url=, output_dir=, assume_yes=)` so the dispatcher can inject CLI args.
- Return `0`/`1` from `main()`, not random exceptions for expected user errors.
- Keep banners in `common/variables.py`.

## Publishing documentation

This repo is the source of truth for its wiki section. GitHub Actions copies `docs/`, `README.md` (as `home.md`), and `CHANGELOG.md` into `ea1fsc/ea1fsc-wiki` under `multi-downloader/`. Workflow: `.github/workflows/sync-docs.yml`. Wiki.js adds its own frontmatter on import — do not put YAML frontmatter in these Markdown files.

Do not copy application code, tests, or secrets into the wiki repo.
