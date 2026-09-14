# How it works

All work happens in-process on your computer. Nothing is queued to a server we run.

```
you → multi_downloader.py
        ├── --gui  → ui/ (PySide6) → app/ services + adapters → platform libraries
        ├── --platform → Instagram | Twitter | YouTube module
        └── menu   → same modules
                    → requests GET (URL reachable?)
                    → platform library (metadata + download)
                    → file on disk
```

## Dispatcher

`multi_downloader.parse_args()` is optional. `--gui` / `-g` imports Qt lazily (`launch_gui`) so a CLI-only install does not need PySide6. If `--platform` is set (and `--gui` is not), `run_non_interactive` calls that module’s `main(...)` once and exits with its return code. Otherwise a `while` loop prints the numbered menu.

Each platform `main()` returns `0` or `1`. The menu treats non-zero as a generic error and continues.

## Shared helpers (`common/`)

| Piece | Role |
| --- | --- |
| `functions.check_url_accessibility` | `requests.get`, success only on HTTP 200 |
| `functions.sanitize_filename` | Strip `\/*?:"<>|` |
| `functions.ask_yes_no` | `y/yes/n/no` |
| `functions.get_valid_download_directory` | Prompt + default Downloads/Descargas |
| `variables` | ASCII banners |
| `check_libraries` | Import-time dependency check |

## Platform adapters

The terminal path calls `Instagram/`, `Twitter/`, and `YouTube/` directly. The GUI uses `app/adapters/` and `app/services/download_service.py` on top of the same libraries (`instaloader`, `yt-dlp`, `pytubefix`).

- **Instagram:** Instaloader context → shortcode → one media URL → `download_pic`.
- **Twitter:** yt-dlp extract then download; merge to mp4 when needed.
- **YouTube:** pytubefix stream filter → user (or first) stream → download → rename.

Libraries talk to third-party sites. HTML, APIs, and rate limits change without notice; that is why downloads can fail after a quiet period. See [Limitations](limitations.md).
