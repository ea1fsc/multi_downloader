"""Background workers for long-running download tasks."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from app.domain.models import DownloadJob, DownloadOutcome, ProgressEvent

if TYPE_CHECKING:
    from app.services.download_service import DownloadService


class DownloadSignals(QObject):
    progress = Signal(object)
    finished = Signal(object)


class DownloadTask(QRunnable):
    """Runs DownloadService.execute in a thread pool worker."""

    def __init__(
        self,
        service: DownloadService,
        job: DownloadJob,
        signals: DownloadSignals,
        cancel_event: threading.Event,
    ) -> None:
        super().__init__()
        self._service = service
        self._job = job
        self._signals = signals
        self._cancel_event = cancel_event

    def run(self) -> None:
        def on_progress(ev: ProgressEvent) -> None:
            self._signals.progress.emit(ev)

        try:
            outcome: DownloadOutcome = self._service.execute(self._job, self._cancel_event, on_progress)
        except Exception as exc:  # noqa: BLE001
            outcome = DownloadOutcome(success=False, message=str(exc))
        self._signals.finished.emit(outcome)


def run_download_task(
    pool: QThreadPool,
    service: DownloadService,
    job: DownloadJob,
    cancel_event: threading.Event,
    signals: DownloadSignals,
) -> None:
    task = DownloadTask(service, job, signals, cancel_event)
    pool.start(task)
