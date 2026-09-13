# Configuration

This program has **no** `.env`, config file, or API keys of its own. Behaviour is set by CLI flags, interactive prompts, and a default download folder.

Do not put cookies, session files, or tokens in the repo. `.gitignore` already ignores `.env` and `.env.*`.

## CLI flags

Parsed in `multi_downloader.py`. Used only when `--platform` is set (non-interactive dispatcher).

| Flag | Values | Meaning |
| --- | --- | --- |
| `--platform` | `instagram`, `twitter`, `youtube` | Run that downloader and exit. Required for one-shot mode. |
| `--url` | string | Post/video URL. If omitted, the module still prompts. |
| `--output` | existing directory | Destination folder. Must already exist and be a directory, or the process exits with code `1`. |
| `--yes` | flag | Skip yes/no confirmations (`assume_yes`). |
| `--mode` | `audio`, `video`, `audio+video` | YouTube only. Ignored for Instagram/Twitter. |

Examples: [Usage](usage.md).

`--yes` does **not** skip the filename `input()` in the downloaders. Press Enter for the default name, or the process waits on stdin.

## Default download directory

If you leave the folder prompt empty, `common/functions.py` picks:

| OS | First existing path, else last candidate |
| --- | --- |
| Linux | `~/Descargas`, then `~/Downloads` |
| Windows / macOS | `~/Downloads`, then `~/Descargas` |

The chosen path must exist and be writable. There is no setting to change this permanently.

`--output` bypasses that prompt when you use `--platform`.

## Confirmations

`ask_yes_no` accepts `y` / `yes` / `n` / `no` (any case). Anything else is rejected and asked again.

## Instagram sessions

The Instagram module builds an anonymous `Instaloader(save_metadata=False, download_comments=False)`. It does **not** load a session file or cookies. Rate-limit `403` responses are a platform issue; see [Troubleshooting](troubleshooting.md).

## Python version

`requires-python = ">=3.12"` in `pyproject.toml`. `.python-version` is `3.12.4` for local tooling (pyenv and similar).
