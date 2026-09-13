# Platforms

What each downloader accepts and writes. Pair with [Usage](usage.md).

## Instagram

**URLs:** `https://www.instagram.com/p/…`, `/reel/…`, or `/tv/…` (optional `www.`, `http` or `https`). Query strings are ignored. Profile URLs and share links without `/p|reel|tv/<shortcode>` are rejected (`extract_shortcode`).

**Engine:** `instaloader.Post.from_shortcode` then `download_pic` for the video URL or image URL. Metadata JSON and comments are not saved.

**Output:** `.mp4` if `post.is_video`, else `.jpg`. Default stem is the shortcode. If `name.jpg` / `name.mp4` already exists, the stem becomes `name_1`, `name_2`, …

**Not implemented:** login, stories, highlights, IGTV listings, carousels as multiple files (one media URL is downloaded), private posts.

**403:** anonymous GraphQL is often rate-limited. See [Troubleshooting](troubleshooting.md).

## Twitter / X

**URLs:** `https://twitter.com/<user>/status/<digits>` or `https://x.com/…` (optional `www.`).

**Engine:** `yt-dlp` metadata (`skip_download`), then download with `format: bestvideo+bestaudio/best` and `merge_output_format: mp4`.

**Preview:** title, uploader, duration, likes when present. You confirm unless `--yes`.

**Rejected:** posts with no `ext` and no `formats` (“does not seem to contain downloadable media”). Text-only tweets will fail here.

**Output:** `{sanitized_title}.%(ext)s` under the chosen directory (usually `.mp4` after merge). Default name is the tweet title or `twitter_video`.

## YouTube

**URLs** (11-character video id):

- `youtube.com/watch?v=`
- `youtu.be/`
- `youtube.com/embed/`
- `youtube.com/v/`
- `youtube.com/shorts/`

Optional `https://` and `www.`. Channel URLs, playlists without a video id, and truncated ids are rejected.

**Engine:** `pytubefix.YouTube`. After metadata, interactive mode lists streams.

| Menu option | `--mode` | Filter |
| --- | --- | --- |
| `1` — video (no audio) | `video` | `only_video=True`, `progressive=False` |
| `2` — audio | `audio` | `only_audio=True` |
| `3` — video with audio | `audio+video` | `progressive=True` (typically ≤720p) |
| `0` | — | Back to URL prompt |

Each listed stream shows type, container, codec, resolution/FPS or ABR, and approximate size when `filesize_mb` exists. You pick an index and confirm, unless `--yes` (first stream).

**Output:** `stream.download()` then rename to your filename, keeping the library’s extension (`.mp4`, `.webm`, `.m4a`, …).

**Known crash:** after printing title/duration/channel, interactive YouTube calls `print(separator)` but `separator` is not defined in `YouTube/youtube_downloader.py`. That raises `NameError` before the “Is this the video you want?” prompt. `--yes` still hits the same `print(separator)` line. See [Troubleshooting](troubleshooting.md).
