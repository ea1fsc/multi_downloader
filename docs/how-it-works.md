# How it works

All work happens in-process on your computer. Nothing is queued to a server we run.

```
you → multi_downloader.py (menu or --platform)
        → Instagram | Twitter | YouTube module
            → requests GET (URL reachable?)
            → platform library (metadata + download)
            → file on disk
```

## Dispatcher

`multi_downloader.parse_args()` is optional. If `--platform` is set, `run_non_interactive` calls that module’s `main(...)` once and exits with its return code. Otherwise a `while` loop prints the numbered menu.

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

There is no extra abstraction on `main`. GUI-style `app/` adapters exist only on `feat/graphical-interface`.

- **Instagram:** Instaloader context → shortcode → one media URL → `download_pic`.
- **Twitter:** yt-dlp extract then download; merge to mp4 when needed.
- **YouTube:** pytubefix stream filter → user (or first) stream → download → rename.

Libraries talk to third-party sites. HTML, APIs, and rate limits change without notice; that is why downloads can fail after a quiet period. See [Limitations](limitations.md).
