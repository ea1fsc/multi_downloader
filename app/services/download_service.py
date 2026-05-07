"""Analyze URLs and run downloads for the desktop UI."""

from __future__ import annotations

import threading
from typing import Callable

from common import functions as func

from app.adapters import instagram_adapter as ig_ad
from app.adapters import twitter_adapter as tw_ad
from app.adapters import youtube_adapter as yt_ad
from app.domain.errors import DownloadError, ValidationError
from app.domain.models import DownloadJob, DownloadOutcome, MediaInfo, Platform, ProgressEvent, ProgressStage, YoutubeKind


ProgressCallback = Callable[[ProgressEvent], None]


class DownloadService:
    """Coordinates accessibility checks, metadata fetch, and platform downloads."""

    def analyze(
        self,
        platform: Platform,
        url: str,
        *,
        youtube_kind: YoutubeKind | None = None,
    ) -> MediaInfo:
        url = url.strip()
        if platform == Platform.YOUTUBE:
            if not yt_ad.is_valid_youtube_url(url):
                raise ValidationError("Invalid YouTube URL.")
            if not func.check_url_accessibility(url, quiet=True):
                raise ValidationError("URL is not reachable (HTTP check failed).")
            yt = yt_ad.load_video(url)
            pv = yt_ad.preview_dict(yt)
            streams: list = []
            kind = youtube_kind or YoutubeKind.AUDIO_VIDEO
            try:
                streams = yt_ad.list_streams_for_kind(yt, kind)
            except Exception:
                streams = []
            return MediaInfo(
                platform=platform,
                url=url,
                title=pv.get("title"),
                subtitle=f"{pv.get('duration', '')} · {pv.get('channel', '')}",
                extra=pv,
                youtube_streams=streams,
                suggested_filename_stem=yt.title,
            )

        if platform == Platform.TWITTER:
            if not tw_ad.is_valid_twitter_url(url):
                raise ValidationError("Invalid Twitter/X status URL.")
            if not func.check_url_accessibility(url, quiet=True):
                raise ValidationError("URL is not reachable (HTTP check failed).")
            info = tw_ad.fetch_info(url)
            tw_ad.ensure_downloadable(info)
            title = str(info.get("title") or "tweet")
            uploader = str(info.get("uploader") or "")
            return MediaInfo(
                platform=platform,
                url=url,
                title=title,
                subtitle=uploader,
                extra={"duration": info.get("duration"), "like_count": info.get("like_count")},
                suggested_filename_stem=title,
            )

        if platform == Platform.INSTAGRAM:
            if not ig_ad.is_valid_instagram_url(url):
                raise ValidationError("Invalid Instagram URL.")
            if not func.check_url_accessibility(url, quiet=True):
                raise ValidationError("URL is not reachable (HTTP check failed).")
            try:
                pv = ig_ad.preview_post(url)
            except Exception as exc:
                raise ValidationError(f"Could not load Instagram post: {exc}") from exc
            cap = pv.get("caption") or ""
            subtitle = f"@{pv.get('owner')} · {'Video' if pv.get('is_video') else 'Image'}"
            return MediaInfo(
                platform=platform,
                url=url,
                title=(cap[:80] + "…") if len(cap) > 80 else cap or "Instagram post",
                subtitle=subtitle,
                extra=pv,
                suggested_filename_stem=str(pv.get("shortcode", "instagram")),
            )

        raise ValidationError("Unsupported platform.")

    def execute(
        self,
        job: DownloadJob,
        cancel_event: threading.Event,
        on_progress: ProgressCallback | None = None,
    ) -> DownloadOutcome:
        def emit(stage: ProgressStage, message: str = "", fraction: float | None = None) -> None:
            if on_progress:
                on_progress(ProgressEvent(stage=stage, message=message, fraction=fraction))

        emit(ProgressStage.PREPARING, "Preparing…", 0.0)

        try:
            if job.platform == Platform.YOUTUBE:
                return self._run_youtube(job, cancel_event, emit)
            if job.platform == Platform.TWITTER:
                return self._run_twitter(job, cancel_event, emit)
            if job.platform == Platform.INSTAGRAM:
                return self._run_instagram(job, cancel_event, emit)
        except (ValidationError, DownloadError) as exc:
            emit(ProgressStage.ERROR, str(exc))
            return DownloadOutcome(success=False, message=str(exc))
        except Exception as exc:  # noqa: BLE001 — surface unexpected failures to UI
            emit(ProgressStage.ERROR, str(exc))
            return DownloadOutcome(success=False, message=str(exc))
        emit(ProgressStage.ERROR, "Unsupported platform.")
        return DownloadOutcome(success=False, message="Unsupported platform.")

    def _progress_bridge(self, on_emit, cancel_event: threading.Event):
        def cb(frac: float | None, msg: str) -> None:
            if cancel_event.is_set():
                return
            on_emit(ProgressStage.DOWNLOADING, msg, frac)

        return cb

    def _run_youtube(self, job: DownloadJob, cancel_event: threading.Event, emit) -> DownloadOutcome:
        if job.youtube_kind is None or job.youtube_stream_index is None:
            raise ValidationError("YouTube requires stream selection.")
        yt = yt_ad.load_video(job.url)
        stream = yt_ad.get_stream_by_index(yt, job.youtube_kind, job.youtube_stream_index)

        def bridge(frac: float | None, msg: str) -> None:
            if cancel_event.is_set():
                return
            emit(ProgressStage.DOWNLOADING, msg, frac)

        path = yt_ad.download_stream(
            yt,
            stream,
            yt.title,
            job.output_dir,
            job.filename_stem,
            cancel_event=cancel_event,
            on_progress=bridge,
        )
        emit(ProgressStage.DONE, f"Finished: {path}", 1.0)
        return DownloadOutcome(success=True, output_path=path)

    def _run_twitter(self, job: DownloadJob, cancel_event: threading.Event, emit) -> DownloadOutcome:
        info = tw_ad.fetch_info(job.url)
        tw_ad.ensure_downloadable(info)
        base = func.sanitize_filename(job.filename_stem or info.get("title") or "twitter_video")
        if not base:
            base = "twitter_video"

        path = tw_ad.download_tweet(
            job.url,
            info,
            job.output_dir,
            base,
            cancel_event,
            on_progress=self._progress_bridge(emit, cancel_event),
        )
        emit(ProgressStage.DONE, f"Finished: {path}", 1.0)
        return DownloadOutcome(success=True, output_path=path)

    def _run_instagram(self, job: DownloadJob, cancel_event: threading.Event, emit) -> DownloadOutcome:
        path = ig_ad.download_post(
            job.url,
            job.output_dir,
            job.filename_stem,
            cancel_event,
            on_progress=self._progress_bridge(emit, cancel_event),
        )
        emit(ProgressStage.DONE, f"Finished: {path}", 1.0)
        return DownloadOutcome(success=True, output_path=path)
