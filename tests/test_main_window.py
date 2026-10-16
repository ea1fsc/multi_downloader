"""Desktop window state tests (offscreen Qt, no network)."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from app.domain.models import MediaInfo, Platform, StreamOption, YoutubeKind  # noqa: E402
from app.services.history_service import HistoryService  # noqa: E402
from app.services.settings_service import SettingsService  # noqa: E402
from ui import main_window as mw  # noqa: E402

URL_A = "https://youtu.be/AAAAAAAAAAA"
URL_B = "https://youtu.be/BBBBBBBBBBB"


def _audio_streams(prefix: str) -> list[StreamOption]:
    return [
        StreamOption(1, f"{prefix} opus 160", YoutubeKind.AUDIO, codec="opus", abr_kbps=160, size_mb=4.3),
        StreamOption(2, f"{prefix} mp4a 128", YoutubeKind.AUDIO, codec="mp4a.40.2", abr_kbps=128, size_mb=3.9),
        StreamOption(3, f"{prefix} mp4a 48", YoutubeKind.AUDIO, codec="mp4a.40.5", abr_kbps=48, size_mb=1.5),
    ]


@pytest.fixture
def window(tmp_path, monkeypatch):
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    monkeypatch.setattr(mw, "SettingsService", lambda: SettingsService(tmp_path / "config"))
    monkeypatch.setattr(mw, "HistoryService", lambda: HistoryService(tmp_path / "data"))
    warnings: list[str] = []
    monkeypatch.setattr(mw.QMessageBox, "warning", lambda _parent, _title, text: warnings.append(text))
    w = mw.MainWindow()
    w._dir_edit.setText(str(tmp_path))
    infos = {
        URL_A: MediaInfo(Platform.YOUTUBE, URL_A, title="Video A", suggested_filename_stem="Video A",
                         youtube_streams=_audio_streams("A")),
        URL_B: MediaInfo(Platform.YOUTUBE, URL_B, title="Video B", suggested_filename_stem="Video B",
                         youtube_streams=_audio_streams("B")),
    }
    w._download_svc.analyze = lambda _plat, url, youtube_kind=None: infos[url]
    w.warnings = warnings
    yield w
    w.close()


def _analyze(w, url: str) -> None:
    w._url_edit.setText(url)
    w._on_analyze()


def test_new_analysis_replaces_auto_filled_name(window):
    _analyze(window, URL_A)
    assert window._name_edit.text() == "Video A"
    _analyze(window, URL_B)
    assert window._name_edit.text() == "Video B"


def test_new_analysis_keeps_name_typed_by_user(window):
    _analyze(window, URL_A)
    window._name_edit.setText("my song")
    _analyze(window, URL_B)
    assert window._name_edit.text() == "my song"


def test_changing_url_invalidates_previous_analysis(window):
    _analyze(window, URL_A)
    window._url_edit.setText(URL_B)
    assert window._stream_combo.count() == 0
    assert window._name_edit.text() == ""
    assert window._validate_job() is None


def test_changing_mode_clears_streams_before_reanalysis(window):
    _analyze(window, URL_A)
    window._yt_kind_combo.setCurrentIndex(window._yt_kind_combo.findData(YoutubeKind.VIDEO))
    assert window._stream_combo.count() == 0
    assert window._validate_job() is None


def test_download_job_matches_analyzed_url(window):
    _analyze(window, URL_A)
    job = window._validate_job()
    assert job is not None
    assert job.url == URL_A
    assert job.filename_stem == "Video A"


def test_default_stream_is_best_quality(window):
    _analyze(window, URL_A)
    assert window._sort_field_combo.currentData() == "abr"
    assert window._sort_order_combo.currentData() == "desc"
    assert window._stream_combo.currentData() == 1


def test_sort_field_follows_mode_default(window):
    window._yt_kind_combo.setCurrentIndex(window._yt_kind_combo.findData(YoutubeKind.VIDEO))
    assert window._sort_field_combo.currentData() == "resolution"
    window._yt_kind_combo.setCurrentIndex(window._yt_kind_combo.findData(YoutubeKind.AUDIO))
    assert window._sort_field_combo.currentData() == "abr"


def test_sort_field_chosen_by_user_is_kept(window):
    window._sort_field_combo.setCurrentIndex(window._sort_field_combo.findData("size"))
    window._yt_kind_combo.setCurrentIndex(window._yt_kind_combo.findData(YoutubeKind.VIDEO))
    assert window._sort_field_combo.currentData() == "size"


def test_download_job_carries_selected_itag(window):
    infos = {URL_A: MediaInfo(Platform.YOUTUBE, URL_A, title="A", suggested_filename_stem="A", youtube_streams=[
        StreamOption(1, "best", YoutubeKind.AUDIO, abr_kbps=160, itag=251),
        StreamOption(2, "worse", YoutubeKind.AUDIO, abr_kbps=48, itag=139),
    ])}
    window._download_svc.analyze = lambda _plat, url, youtube_kind=None: infos[url]
    _analyze(window, URL_A)
    job = window._validate_job()
    assert job.youtube_itag == 251


def _answer(monkeypatch, button):
    monkeypatch.setattr(mw.QMessageBox, "question", lambda *_a, **_k: button)


def test_close_without_download_is_accepted(window):
    assert window.close() is True


def test_close_during_download_can_be_refused(window, monkeypatch):
    window._download_running = True
    _answer(monkeypatch, mw.QMessageBox.StandardButton.No)
    assert window.close() is False
    assert not window._cancel_event.is_set()
    window._download_running = False


def test_close_during_download_cancels_it(window, monkeypatch):
    window._download_running = True
    _answer(monkeypatch, mw.QMessageBox.StandardButton.Yes)
    assert window.close() is True
    assert window._cancel_event.is_set()


HOSTILE = '<a href="https://evil.example">Click to update</a><img src="file:///etc/hostname">'


def _rendered_text(rich_text: str) -> str:
    from PySide6.QtGui import QTextDocument

    doc = QTextDocument()
    doc.setHtml(rich_text)
    return doc.toPlainText()


def test_remote_title_is_shown_literally(window):
    infos = {URL_A: MediaInfo(Platform.YOUTUBE, URL_A, title=HOSTILE, subtitle="<i>uploader</i>",
                              youtube_streams=_audio_streams("A"))}
    window._download_svc.analyze = lambda _plat, url, youtube_kind=None: infos[url]
    _analyze(window, URL_A)
    shown = _rendered_text(window._info_label.text())
    assert HOSTILE in shown
    assert "<i>uploader</i>" in shown


def test_log_lines_are_plain_text(window):
    window._log_line(f"[analyze] {HOSTILE}")
    assert window._log.toPlainText().endswith(HOSTILE)


def test_analyze_error_dialog_shows_text_literally(window, monkeypatch):
    shown: list[str] = []
    monkeypatch.setattr(mw.QMessageBox, "warning", lambda _p, _t, text: shown.append(text))

    def failing(*_a, **_k):
        raise RuntimeError(HOSTILE)

    window._download_svc.analyze = failing
    _analyze(window, URL_A)
    assert _rendered_text(shown[-1]) == HOSTILE
