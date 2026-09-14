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
| `test_core_helpers.py` | Filename sanitize, Instagram shortcode/stems, yes/no, download dir, URL validators |
| `test_platform_flows.py` | `main()` success paths with mocks (no live I/O) |
| `test_cli_args.py` | `--platform` dispatcher, `--gui` / `-g`, invalid `--output` |
| `test_check_libraries.py` | Import diagnostics |
| `test_download_service.py` | GUI download service and history store (no Qt window) |
| `test_packaging_helpers.py` | CHANGELOG section extraction for releases |

Do not add tests that hit real Instagram/Twitter/YouTube.

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
| `.github/workflows/release.yml` | Tagged-release binaries and packages |

Standalone builds: [Building](building.md).

## Conventions

- Platform `main(..., preset_url=, output_dir=, assume_yes=)` so the dispatcher can inject CLI args.
- Return `0`/`1` from `main()`, not random exceptions for expected user errors.
- Keep banners in `common/variables.py`.

## Publishing documentation

This repo is the source of truth for its wiki section. GitHub Actions copies `docs/`, `README.md` (as `home.md`), and `CHANGELOG.md` into `ea1fsc/ea1fsc-wiki` under `multi-downloader/`. Workflow: `.github/workflows/sync-docs.yml`. Wiki.js adds its own frontmatter on import — do not put YAML frontmatter in these Markdown files.

Do not copy application code, tests, or secrets into the wiki repo.
