# Troubleshooting

Work top-down: venv → libraries import → URL format → HTTP 200 → platform library error.

## Process will not start

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| `python: command not found` | No Python on PATH | Install 3.12+ or use `python3`. |
| Syntax / version errors | Python older than 3.12 | See [Installation](installation.md). |
| `ModuleNotFoundError` | Venv not active or deps missing | `pip install -r requirements.txt`, then `python common/check_libraries.py`. |

## URL rejected immediately

The regex never matched. Use a **post or video** URL:

- Instagram: `/p/`, `/reel/`, or `/tv/` plus shortcode — not a profile.
- Twitter/X: `/status/<digits>` on `twitter.com` or `x.com`.
- YouTube: watch / `youtu.be` / shorts / embed with an 11-character id.

Details: [Platforms](platforms.md).

## “URL returned status code …” / accessibility check fails

`requests.get` did not get HTTP 200. Causes: private content, region block, login wall, dead link, or the site blocking datacenter IPs. Open the same URL in a browser on that machine. There is no cookie flag in this CLI.

## Instagram HTTP 403

Anonymous `graphql/query` is often rate-limited. The module prints that explanation when `"403"` appears in the exception text.

- Wait a few minutes; do not hammer retries.
- Try another public post.
- This app does **not** load an Instaloader session file. Logging in with Instaloader yourself is outside this wrapper.

## Twitter: no downloadable media

The tweet has no `ext`/`formats` in yt-dlp. Images-only or text posts are not handled. Video posts can still fail if Twitter/yt-dlp extractor changes — upgrade `yt-dlp` in the venv.

## YouTube: `NameError: name 'separator' is not defined`

After title/duration/channel are printed, `YouTube/youtube_downloader.py` calls `print(separator)` but never defines `separator`. That crash is in current `main`. It is not a bad URL. Track a code fix; this documentation does not patch it.

If you reach stream listing, empty lists mean that `--mode` has no matching pytubefix streams (for example progressive muxed above 720p).

## Invalid output directory

With `--output`, the path must exist **before** start (`os.path.isdir`). Create the folder yourself.

In interactive mode, a missing or non-writable path is rejected and you are prompted again.

## Filename collisions

Instagram appends `_1`, `_2`, … Twitter/YouTube may overwrite depending on the library if you reuse the same name. Choose a new name or a new folder.

## Download another file / wrong URL reused

Older YouTube builds stuck on the first URL ([issue #3](https://github.com/ea1fsc/multi_downloader/issues/3)). Current YouTube loop asks “From the same URL?” after each file. Answer `n` to paste a new link.

## Tests fail on a clean clone

```bash
pip install -r requirements.txt
pytest
```

Need Python 3.12+. Tests monkeypatch network; they should not hit live Instagram/Twitter/YouTube. If they do, you changed the suite.

## Still stuck

Open a bug report with OS, Python version, platform, full URL **pattern** (you can redact ids), and the traceback. Do not paste session cookies or `.env` files.
