# Platforms

What each downloader accepts and writes. Pair with [Usage](usage.md).

## Instagram

**URLs:** `https://www.instagram.com/p/…`, `/reel/…`, or `/tv/…` (optional `www.`, `http` or `https`). Query strings are ignored. Profile URLs and share links without `/p|reel|tv/<shortcode>` are rejected (`extract_shortcode`).

**Engine:** `instaloader.Post.from_shortcode`, then the video URL or image URL is fetched through Instaloader’s session. Metadata JSON and comments are not saved.

**Output:** the extension comes from the server’s `Content-Type` (`.jpg`, `.webp`, `.heic`, `.mp4`, …), falling back to `.mp4` for videos and `.jpg` for images. Default stem is the shortcode. Typing `name.jpg` for an image (or `name.mp4` for a video) does not duplicate the extension. If the file already exists, the stem becomes `name_1`, `name_2`, …; an existing file is never skipped or overwritten. The CLI and the GUI history show the real saved path.

**Not implemented:** login, stories, highlights, IGTV listings, carousels as multiple files (one media URL is downloaded), private posts.

**403:** anonymous GraphQL is often rate-limited. See [Troubleshooting](troubleshooting.md).

## Twitter / X

**URLs:** `https://twitter.com/<user>/status/<digits>` or `https://x.com/…` (optional `www.` or `mobile.`). `…/i/web/status/<digits>` share links work too.

**Engine:** `yt-dlp` metadata (`skip_download`), then download with `format: bestvideo+bestaudio/best` and `merge_output_format: mp4`.

**Preview:** title, uploader, duration, likes when present. You confirm unless `--yes`.

**Rejected:** posts with no `ext` and no `formats` (“does not seem to contain downloadable media”). Text-only tweets will fail here.

**Output:** `{sanitized_title}.%(ext)s` under the chosen directory (usually `.mp4` after merge). Default name is the tweet title or `twitter_video`. A trailing `.mp4` in your name is not duplicated, and `%` in names is kept literally. The CLI and the GUI history show the saved file path.

## YouTube

**URLs** (11-character video id):

- `youtube.com/watch?v=`
- `youtu.be/`
- `youtube.com/embed/`
- `youtube.com/v/`
- `youtube.com/shorts/`
- `youtube.com/live/`

Optional `https://` and `www.`, `m.`, or `music.` host prefix. Channel URLs, playlists without a video id, and truncated ids are rejected.

**Engine:** `pytubefix.YouTube`. After metadata, interactive mode lists streams.

| Menu option | `--mode` | Filter |
| --- | --- | --- |
| `1` — video (no audio) | `video` | `only_video=True`, `progressive=False` |
| `2` — audio | `audio` | `only_audio=True` |
| `3` — video with audio | `audio+video` | `progressive=True` (usually only 360p) |
| `0` | — | Back to URL prompt |

pytubefix’s default client returns no progressive streams. In `audio+video` mode the app retries with the `ANDROID`, `ANDROID_VR`, and `MWEB` clients and uses the first one whose progressive stream URL actually answers; some clients list a stream that YouTube then blocks with HTTP 403. pytubefix may print “PoToken” / “botGuard” notices during that retry; they are informational.

Streams are listed best quality first: audio by bitrate, video by resolution then FPS. Each listed stream shows type, container, codec, resolution/FPS or ABR, and approximate size when it can be fetched (otherwise `N/A`). You pick an index and confirm, unless `--yes` (stream `1`, the best one). The GUI preselects the best stream too: by default it sorts by bitrate (audio) or resolution (video), descending. You can change the sort; a sort field you pick is kept when you switch modes.

**Output:** the stream is downloaded to a hidden temporary file (`.multi-downloader-<id>.part`) in the chosen folder and moved to your filename only when complete; a cancelled, failed or incomplete download (fewer bytes than YouTube announced) removes it and reports an error. No other file in the folder is touched. The extension follows the stream’s real container (MIME type): `.m4a` for MP4 audio, `.webm` for WebM/Opus audio, `.mp4` for MP4 video. If your name already ends with that extension, it is not added twice. An existing file with the same name is overwritten.
