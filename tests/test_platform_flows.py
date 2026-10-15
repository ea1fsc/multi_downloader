"""Behavior tests for platform downloader flows."""

from __future__ import annotations

from Instagram import instagram_downloader as ig
from Twitter import twitter_downloader as tw
from YouTube import youtube_downloader as yt


def test_instagram_main_success_exit(monkeypatch):
    monkeypatch.setattr(ig, "get_instagram_url", lambda: "https://www.instagram.com/p/ABC123DEF45/")
    monkeypatch.setattr(ig.func, "check_url_accessibility", lambda _url: True)
    monkeypatch.setattr(ig, "download_instagram_post", lambda _url, output_dir=None: True)
    monkeypatch.setattr(ig.func, "ask_yes_no", lambda _prompt: False)
    assert ig.main() == 0


def test_twitter_main_returns_zero_after_download(monkeypatch):
    monkeypatch.setattr(tw, "request_twitter_url", lambda: "https://x.com/user/status/1234567890")
    monkeypatch.setattr(tw.func, "check_url_accessibility", lambda _url: True)
    monkeypatch.setattr(tw, "get_tweet_info", lambda _url: {"ext": "mp4", "title": "a", "formats": [1]})
    monkeypatch.setattr(tw, "confirm_tweet", lambda _info: True)
    monkeypatch.setattr(
        tw,
        "download_tweet_video",
        lambda _url, _info, output_dir=None: (True, "/tmp"),
    )
    monkeypatch.setattr(tw, "ask_download_another", lambda: False)
    assert tw.main() == 0


def test_youtube_main_returns_zero_when_user_stops(monkeypatch):
    class FakeYt:
        title = "video-title"

    monkeypatch.setattr(yt, "request_url", lambda: "https://youtu.be/dQw4w9WgXcQ")
    monkeypatch.setattr(yt.func, "check_url_accessibility", lambda _url: True)
    monkeypatch.setattr(yt, "build_and_confirm_yt", lambda _url, assume_yes=False: (True, FakeYt()))
    monkeypatch.setattr(yt, "ask_mode", lambda: "audio")
    monkeypatch.setattr(yt, "get_streams_by_format", lambda _yt, _kind: ["stream"])
    monkeypatch.setattr(yt, "choose_stream", lambda _streams, _label, auto_select=False: "stream")
    monkeypatch.setattr(yt, "download_stream", lambda _stream, _title, output_dir=None: True)
    monkeypatch.setattr(yt, "ask_another_and_same_url", lambda: (False, False))
    assert yt.main() == 0


class _FakeStream:
    def __init__(self, abr=None, resolution=None, fps=None):
        self.abr = abr
        self.resolution = resolution
        self.fps = fps
        self.mime_type = "audio/mp4"
        self.codecs = ["codec"]
        self.filesize_mb = 1.0


class _FakeStreamQuery(list):
    def filter(self, **_kwargs):
        return self


class _FakeYoutube:
    def __init__(self, streams):
        self.streams = _FakeStreamQuery(streams)


def test_youtube_audio_streams_sorted_by_bitrate_desc():
    low, high, mid = _FakeStream(abr="48kbps"), _FakeStream(abr="160kbps"), _FakeStream(abr="128kbps")
    streams = yt.get_streams_by_format(_FakeYoutube([low, high, mid]), "audio")
    assert streams == [high, mid, low]


def test_youtube_video_streams_sorted_by_resolution_then_fps():
    hd30 = _FakeStream(resolution="1080p", fps=30)
    hd60 = _FakeStream(resolution="1080p", fps=60)
    sd = _FakeStream(resolution="480p", fps=30)
    unknown = _FakeStream()
    streams = yt.get_streams_by_format(_FakeYoutube([sd, unknown, hd30, hd60]), "video")
    assert streams == [hd60, hd30, sd, unknown]


def test_youtube_auto_select_picks_best_audio():
    low, high = _FakeStream(abr="48kbps"), _FakeStream(abr="160kbps")
    streams = yt.get_streams_by_format(_FakeYoutube([low, high]), "audio")
    assert yt.choose_stream(streams, "audio", auto_select=True) is high


def test_youtube_stream_extension_uses_real_container():
    def stream(mime):
        s = _FakeStream()
        s.mime_type = mime
        return s

    assert yt.stream_extension(stream("audio/mp4"), "x.m4a") == ".m4a"
    assert yt.stream_extension(stream("audio/webm"), "x.m4a") == ".webm"
    assert yt.stream_extension(stream("video/mp4"), "x.mp4") == ".mp4"
    assert yt.stream_extension(stream(None), "x.m4a") == ".m4a"


def test_youtube_final_file_stem_strips_extension_and_never_empty():
    assert yt.final_file_stem("song.webm", ".webm") == "song"
    assert yt.final_file_stem("", ".webm") == "youtube_media"


def test_preset_url_must_match_platform(monkeypatch):
    def unreachable(_url):
        raise AssertionError("network check must not run for an invalid URL")

    for module in (ig, tw, yt):
        monkeypatch.setattr(module.func, "check_url_accessibility", unreachable)
    assert yt.main(preset_url="https://example.com/video", assume_yes=True) == 1
    assert tw.main(preset_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", assume_yes=True) == 1
    assert ig.main(preset_url="https://example.com/p/ABC/", assume_yes=True) == 1


def test_twitter_cli_reports_saved_file(monkeypatch, tmp_path):
    class FakeYDL:
        def __init__(self, opts):
            self.opts = opts

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def download(self, _urls):
            for hook in self.opts["post_hooks"]:
                hook(str(tmp_path / "clip.mp4"))

    monkeypatch.setattr(tw.yt_dlp, "YoutubeDL", FakeYDL)
    monkeypatch.setattr("builtins.input", lambda _prompt: "")
    ok, path = tw.download_tweet_video("https://x.com/u/status/1", {"title": "clip"}, output_dir=str(tmp_path))
    assert ok and path == str(tmp_path / "clip.mp4")


class _ProgressiveQuery(list):
    def filter(self, progressive=False, **_kwargs):
        return _ProgressiveQuery(s for s in self if s.is_progressive) if progressive else self

    def first(self):
        return self[0] if self else None


class _ProgressiveStream:
    def __init__(self, progressive, blocked=False):
        self.is_progressive = progressive
        self.itag = 18
        self._blocked = blocked

    @property
    def filesize(self):
        if self._blocked:
            raise RuntimeError("HTTP Error 403: Forbidden")
        return 1024

    @property
    def filesize_mb(self):
        return self.filesize / 1024 / 1024


class _ClientYoutube:
    def __init__(self, client, progressive, blocked=False):
        self.client = client
        self.streams = _ProgressiveQuery([_ProgressiveStream(progressive, blocked)])


def test_progressive_falls_back_to_client_with_progressive_streams(monkeypatch):
    clients_tried = []

    def fake_youtube(_url, client):
        clients_tried.append(client)
        # ANDROID lists nothing; ANDROID_VR lists itag 18 but YouTube answers 403; MWEB works.
        return _ClientYoutube(client, progressive=client != "ANDROID", blocked=client == "ANDROID_VR")

    monkeypatch.setattr(yt.pyt, "YouTube", fake_youtube)
    result = yt.with_progressive_streams("https://youtu.be/x", _ClientYoutube("VISION_OS", progressive=False))
    assert result.client == "MWEB"
    assert clients_tried == ["ANDROID", "ANDROID_VR", "MWEB"]


def test_stream_size_mb_is_none_when_lookup_fails():
    assert yt.stream_size_mb(_ProgressiveStream(True, blocked=True)) is None
    assert yt.stream_size_mb(_ProgressiveStream(True)) == 1024 / 1024 / 1024


def test_display_stream_info_survives_blocked_size(capsys):
    stream = _ProgressiveStream(True, blocked=True)
    stream.mime_type, stream.codecs, stream.resolution, stream.fps, stream.abr = "video/mp4", ["avc1"], "360p", 30, None
    yt.display_stream_info(1, stream, "audio+video")
    assert "Approx size: N/A" in capsys.readouterr().out


def test_progressive_keeps_default_client_when_it_has_streams(monkeypatch):
    monkeypatch.setattr(yt.pyt, "YouTube", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("no fallback")))
    original = _ClientYoutube("VISION_OS", progressive=True)
    assert yt.with_progressive_streams("https://youtu.be/x", original) is original
