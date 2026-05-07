"""Primary desktop window: download flow, history, and settings."""

from __future__ import annotations

import os
import threading
from pathlib import Path

from PySide6.QtCore import QThreadPool, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.domain.models import DownloadJob, Platform, ProgressStage, YoutubeKind
from app.services.download_service import DownloadService
from app.services.history_service import HistoryService
from app.services.settings_service import SettingsService
from common import functions as func
from ui.workers import DownloadSignals, run_download_task


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Multi Downloader")
        self.resize(920, 640)

        self._settings_svc = SettingsService()
        self._history_svc = HistoryService()
        self._download_svc = DownloadService()
        self._settings = self._settings_svc.load()

        self._pool = QThreadPool.globalInstance()
        self._cancel_event = threading.Event()
        self._download_signals = DownloadSignals()
        self._download_signals.progress.connect(self._on_download_progress)
        self._download_signals.finished.connect(self._on_download_finished)

        self._last_job: DownloadJob | None = None
        self._last_analyzed_title: str | None = None

        self._build_ui()
        self._apply_settings_to_ui()
        self._analyze_timer = QTimer(self)
        self._analyze_timer.setSingleShot(True)
        self._analyze_timer.setInterval(500)
        self._analyze_timer.timeout.connect(self._on_auto_analyze_timeout)

    def _build_ui(self) -> None:
        tabs = QTabWidget()
        tabs.addTab(self._build_download_tab(), "Download")
        tabs.addTab(self._build_history_tab(), "History")
        tabs.addTab(self._build_settings_tab(), "Settings")
        self.setCentralWidget(tabs)

    def _build_download_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        form = QFormLayout()
        self._download_form = form
        self._platform_combo = QComboBox()
        self._platform_combo.addItem("YouTube", Platform.YOUTUBE)
        self._platform_combo.addItem("Twitter/X", Platform.TWITTER)
        self._platform_combo.addItem("Instagram", Platform.INSTAGRAM)
        self._platform_combo.currentIndexChanged.connect(self._on_platform_changed)

        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText("Paste media URL…")

        self._yt_kind_combo = QComboBox()
        self._yt_kind_combo.addItem("Audio only", YoutubeKind.AUDIO)
        self._yt_kind_combo.addItem("Video only (no audio)", YoutubeKind.VIDEO)
        self._yt_kind_combo.addItem("Video + audio (progressive ≤720p)", YoutubeKind.AUDIO_VIDEO)
        self._yt_kind_combo.currentIndexChanged.connect(self._schedule_auto_analyze)

        self._analyze_btn = QPushButton("Analyze")
        self._analyze_btn.clicked.connect(self._on_analyze)

        row_url = QHBoxLayout()
        row_url.addWidget(self._url_edit, stretch=1)
        row_url.addWidget(self._analyze_btn)

        form.addRow("Platform", self._platform_combo)
        form.addRow("YouTube mode", self._yt_kind_combo)
        form.addRow("URL", row_url)

        self._info_label = QLabel("Analyze a URL to see details and available streams.")
        self._info_label.setWordWrap(True)

        self._stream_combo = QComboBox()
        self._stream_combo.setEnabled(False)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Optional custom file name (without extension)")

        self._dir_edit = QLineEdit()
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse_output_dir)
        dir_row = QHBoxLayout()
        dir_row.addWidget(self._dir_edit, stretch=1)
        dir_row.addWidget(browse)

        form.addRow("Details", self._info_label)
        form.addRow("Stream", self._stream_combo)
        form.addRow("File name", self._name_edit)
        form.addRow("Save to", dir_row)

        layout.addLayout(form)

        self._progress = QProgressBar()
        self._progress.setRange(0, 1000)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMinimumHeight(180)

        btn_row = QHBoxLayout()
        self._download_btn = QPushButton("Download")
        self._download_btn.clicked.connect(self._on_download)
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self._on_cancel)
        btn_row.addWidget(self._download_btn)
        btn_row.addWidget(self._cancel_btn)
        btn_row.addStretch(1)

        layout.addWidget(self._progress)
        layout.addLayout(btn_row)
        layout.addWidget(QLabel("Log"))
        layout.addWidget(self._log)

        self._on_platform_changed()
        return page

    def _history_title_for_entry(self) -> str | None:
        return self._last_analyzed_title or self._name_edit.text().strip() or None

    def _build_history_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self._history_table = QTableWidget(0, 6)
        self._history_table.setHorizontalHeaderLabels(
            ["When", "Platform", "URL", "Title", "Status", "Output"]
        )
        self._history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._refresh_history)
        open_folder = QPushButton("Open output folder")
        open_folder.clicked.connect(self._open_selected_history_folder)
        clear_history = QPushButton("Clear history")
        clear_history.clicked.connect(self._clear_history)

        row = QHBoxLayout()
        row.addWidget(refresh)
        row.addWidget(open_folder)
        row.addWidget(clear_history)
        row.addStretch(1)

        layout.addLayout(row)
        layout.addWidget(self._history_table)
        self._refresh_history()
        return page

    def _build_settings_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        box = QGroupBox("Default download folder")
        form = QFormLayout(box)
        self._settings_dir_edit = QLineEdit()
        b = QPushButton("Browse…")
        b.clicked.connect(self._browse_settings_dir)
        row = QHBoxLayout()
        row.addWidget(self._settings_dir_edit, stretch=1)
        row.addWidget(b)
        form.addRow("Folder", row)

        save = QPushButton("Save settings")
        save.clicked.connect(self._save_settings)

        layout.addWidget(box)
        layout.addWidget(save)
        layout.addStretch(1)
        return page

    def _apply_settings_to_ui(self) -> None:
        default_dir = self._settings.default_download_dir or func.get_default_download_directory()
        if default_dir:
            self._dir_edit.setText(default_dir)
            self._settings_dir_edit.setText(default_dir)

    def _on_platform_changed(self) -> None:
        plat = self._current_platform()
        is_yt = plat == Platform.YOUTUBE
        yt_mode_label = self._download_form.labelForField(self._yt_kind_combo)
        stream_label = self._download_form.labelForField(self._stream_combo)
        if yt_mode_label is not None:
            yt_mode_label.setVisible(is_yt)
        if stream_label is not None:
            stream_label.setVisible(is_yt)
        self._yt_kind_combo.setVisible(is_yt)
        self._stream_combo.setVisible(is_yt)
        if not is_yt:
            self._stream_combo.clear()
            self._stream_combo.setEnabled(False)
        else:
            self._stream_combo.setEnabled(self._stream_combo.count() > 0)
        # Reset source-specific fields when user changes download source.
        self._url_edit.clear()
        self._name_edit.clear()
        self._last_analyzed_title = None
        self._info_label.setText("Analyze a URL to see details and available streams.")

    def _current_platform(self) -> Platform:
        raw = self._platform_combo.currentData()
        return raw if isinstance(raw, Platform) else Platform(raw)

    def _current_youtube_kind(self) -> YoutubeKind:
        raw = self._yt_kind_combo.currentData()
        return raw if isinstance(raw, YoutubeKind) else YoutubeKind(raw)

    def _browse_output_dir(self) -> None:
        start = self._dir_edit.text().strip() or func.get_default_download_directory() or ""
        path = QFileDialog.getExistingDirectory(self, "Select download folder", start)
        if path:
            self._dir_edit.setText(path)

    def _browse_settings_dir(self) -> None:
        start = self._settings_dir_edit.text().strip() or func.get_default_download_directory() or ""
        path = QFileDialog.getExistingDirectory(self, "Select default folder", start)
        if path:
            self._settings_dir_edit.setText(path)

    def _save_settings(self) -> None:
        path = self._settings_dir_edit.text().strip()
        self._settings.default_download_dir = path or None
        self._settings_svc.save(self._settings)
        self._dir_edit.setText(path)
        QMessageBox.information(self, "Settings", "Settings saved.")

    def _log_line(self, msg: str) -> None:
        self._log.append(msg)

    def _platform_display_name(self, platform: Platform) -> str:
        if platform == Platform.YOUTUBE:
            return "YouTube"
        if platform == Platform.INSTAGRAM:
            return "Instagram"
        return "Twitter/X"

    def _on_analyze(self) -> None:
        self._analyze_impl(show_dialogs=True)

    def _schedule_auto_analyze(self) -> None:
        # Debounce auto-analysis while user is typing/changing options.
        if self._current_platform() != Platform.YOUTUBE:
            return
        if not self._url_edit.text().strip():
            return
        self._analyze_timer.start()

    def _on_auto_analyze_timeout(self) -> None:
        self._analyze_impl(show_dialogs=False)

    def _analyze_impl(self, *, show_dialogs: bool) -> None:
        url = self._url_edit.text().strip()
        if not url:
            return
        plat = self._current_platform()
        self._stream_combo.clear()
        self._stream_combo.setEnabled(plat == Platform.YOUTUBE)
        try:
            kind = self._current_youtube_kind() if plat == Platform.YOUTUBE else None
            info = self._download_svc.analyze(plat, url, youtube_kind=kind)
        except Exception as exc:
            if show_dialogs:
                QMessageBox.warning(self, "Analyze failed", str(exc))
            else:
                self._log_line(f"[analyze] {exc}")
            return

        self._last_analyzed_title = info.title

        extra = []
        if info.title:
            extra.append(f"<b>{info.title}</b>")
        if info.subtitle:
            extra.append(info.subtitle)
        self._info_label.setText("<br/>".join(extra) if extra else "Ready.")

        if plat == Platform.YOUTUBE:
            self._stream_combo.clear()
            for opt in info.youtube_streams:
                self._stream_combo.addItem(opt.label, opt.index)
            self._stream_combo.setEnabled(len(info.youtube_streams) > 0)
            if not info.youtube_streams:
                QMessageBox.warning(
                    self,
                    "No streams",
                    "No streams found for this mode. Try another YouTube mode.",
                )
        if info.suggested_filename_stem and not self._name_edit.text().strip():
            self._name_edit.setText(info.suggested_filename_stem)

        platform_name = self._platform_display_name(plat)
        if plat == Platform.YOUTUBE:
            mode_label = self._current_youtube_kind().value
            self._log_line(
                f"Analyzed ({platform_name}): url={url} | mode={mode_label} | streams={len(info.youtube_streams)}"
            )
        else:
            self._log_line(f"Analyzed ({platform_name}): url={url}")

    def _validate_job(self) -> DownloadJob | None:
        url = self._url_edit.text().strip()
        out = self._dir_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Missing URL", "Enter a URL.")
            return None
        if not out or not os.path.isdir(out):
            QMessageBox.warning(self, "Output folder", "Choose a valid output directory.")
            return None
        if not os.access(out, os.W_OK):
            QMessageBox.warning(self, "Output folder", "Output directory is not writable.")
            return None

        plat = self._current_platform()
        name = self._name_edit.text().strip() or None

        if plat == Platform.YOUTUBE:
            idx = self._stream_combo.currentData()
            kind = self._current_youtube_kind()
            if idx is None:
                QMessageBox.warning(self, "Stream", "Analyze and pick a stream.")
                return None
            return DownloadJob(
                platform=plat,
                url=url,
                output_dir=out,
                filename_stem=name,
                youtube_kind=kind,
                youtube_stream_index=int(idx),
            )

        return DownloadJob(platform=plat, url=url, output_dir=out, filename_stem=name)

    def _on_download(self) -> None:
        job = self._validate_job()
        if not job:
            return

        self._last_job = job
        self._cancel_event = threading.Event()
        self._download_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self._progress.setRange(0, 1000)
        self._progress.setValue(0)
        self._log_line("Starting download…")

        run_download_task(self._pool, self._download_svc, job, self._cancel_event, self._download_signals)

    def _on_cancel(self) -> None:
        self._cancel_event.set()
        self._log_line("Cancellation requested…")

    def _on_download_progress(self, ev: object) -> None:
        from app.domain.models import ProgressEvent

        if not isinstance(ev, ProgressEvent):
            return
        self._log_line(f"[{ev.stage.value}] {ev.message}")
        if ev.fraction is not None:
            if self._progress.minimum() == 0 and self._progress.maximum() == 0:
                self._progress.setRange(0, 1000)
            self._progress.setValue(int(ev.fraction * 1000))
        elif ev.stage == ProgressStage.DOWNLOADING:
            # Some providers do not expose bytes/percentage. Show busy indicator.
            self._progress.setRange(0, 0)

    def _on_download_finished(self, outcome: object) -> None:
        from app.domain.models import DownloadOutcome

        self._download_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        if self._progress.minimum() == 0 and self._progress.maximum() == 0:
            self._progress.setRange(0, 1000)

        if isinstance(outcome, DownloadOutcome):
            job = self._last_job
            title_guess = self._history_title_for_entry()
            if outcome.success:
                self._progress.setValue(1000)
                self._log_line(f"Done: {outcome.output_path}")
                if job:
                    self._history_svc.add_entry(
                        platform=job.platform,
                        url=job.url,
                        title=title_guess,
                        output_path=outcome.output_path,
                        status="success",
                    )
            else:
                self._log_line(f"Failed: {outcome.message}")
                if job:
                    self._history_svc.add_entry(
                        platform=job.platform,
                        url=job.url,
                        title=title_guess,
                        output_path=None,
                        status="error",
                        error_message=outcome.message,
                    )
        self._refresh_history()

    def _clear_history(self) -> None:
        answer = QMessageBox.question(
            self,
            "Clear history",
            "Delete all download history entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._history_svc.clear()
        self._refresh_history()
        self._log_line("History cleared.")

    def _refresh_history(self) -> None:
        entries = self._history_svc.list_entries()
        self._history_table.setRowCount(0)
        for e in entries:
            row = self._history_table.rowCount()
            self._history_table.insertRow(row)
            self._history_table.setItem(row, 0, QTableWidgetItem(e.created_at.isoformat()))
            self._history_table.setItem(row, 1, QTableWidgetItem(self._platform_display_name(e.platform)))
            self._history_table.setItem(row, 2, QTableWidgetItem(e.url))
            self._history_table.setItem(row, 3, QTableWidgetItem(e.title or ""))
            self._history_table.setItem(row, 4, QTableWidgetItem(e.status))
            self._history_table.setItem(row, 5, QTableWidgetItem(e.output_path or ""))

    def _open_selected_history_folder(self) -> None:
        rows = self._history_table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "History", "Select a row first.")
            return
        r = rows[0].row()
        path_item = self._history_table.item(r, 5)
        if not path_item or not path_item.text():
            QMessageBox.information(self, "History", "No output path for this entry.")
            return
        p = Path(path_item.text())
        folder = p if p.is_dir() else p.parent
        if folder.is_dir():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder.resolve())))
