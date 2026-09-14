# Usage

Audience: anyone running the app on their computer.

Exit the terminal menu with `0` or `Ctrl+C`. Both print a short goodbye line.

## Interactive menu

From the repo root, with the venv active:

```bash
python multi_downloader.py
```

| Input | Action |
| --- | --- |
| `1` | Instagram downloader |
| `2` | Twitter/X downloader |
| `3` | YouTube downloader |
| `0` | Exit |

Invalid input prints “Invalid option” and shows the menu again. If a platform `main()` returns non-zero, you see “An error has occurred. Please try again.” and stay in the menu.

## Desktop GUI

Install [GUI extras](installation.md) first. Then:

```bash
python multi_downloader.py --gui
python multi_downloader.py -g
```

Tabs: **Download** (analyze URL, pick YouTube stream, destination), **History** (SQLite log), **Settings** (default folder). Downloads run in a background thread. `--gui` ignores `--platform` / `--url` and the other one-shot flags.

## Direct module start

You can also start a module without the menu:

```bash
python Instagram/instagram_downloader.py
python Twitter/twitter_downloader.py
python YouTube/youtube_downloader.py
```

## Shared prompts

Every platform:

1. Asks for a URL (unless `--url` was passed).
2. GETs the URL with `requests` (`check_url_accessibility`). HTTP 200 is required before metadata fetch.
3. Asks for a destination directory (unless `--output` was passed). Enter = [default Downloads](configuration.md).
4. Asks for a file name. Enter = platform default (shortcode, tweet title, or video title). Characters `\ / * ? : " < > |` become `_`.

Yes/no questions accept `y`/`yes`/`n`/`no`.

After a successful interactive download, Instagram and Twitter ask whether to download another post. YouTube asks whether to download another item and whether to reuse the same URL.

## Non-interactive (`--platform`)

```bash
python multi_downloader.py --platform <instagram|twitter|youtube> [options]
```

| Flag | Notes |
| --- | --- |
| `--url` | Full post/video URL. |
| `--output` | Directory that **already exists**. |
| `--yes` | Skip tweet/video confirmations and YouTube stream picking (first stream in the list). |
| `--mode` | YouTube: `audio`, `video`, or `audio+video`. |

Exit codes: `0` success, `1` bad output path, unreachable URL, failed download, or declined confirmation in one-shot mode.

Filename prompts still run. For scripts, pipe a newline or run under a TTY and press Enter.

### Examples

YouTube audio, skip confirmations:

```bash
python multi_downloader.py --platform youtube \
  --url "https://youtu.be/dQw4w9WgXcQ" \
  --mode audio --output "/tmp" --yes
```

Instagram post:

```bash
python multi_downloader.py --platform instagram \
  --url "https://www.instagram.com/p/SHORTCODE/" \
  --output "/tmp" --yes
```

Twitter/X video:

```bash
python multi_downloader.py --platform twitter \
  --url "https://x.com/user/status/1234567890" \
  --output "/tmp" --yes
```

`--platform` without a valid choice is rejected by argparse. `--mode` on Instagram/Twitter is ignored.

URL formats and per-platform behaviour: [Platforms](platforms.md).
