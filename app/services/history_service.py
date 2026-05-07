"""SQLite-backed download history."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from platformdirs import user_data_dir

from app.domain.models import HistoryEntry, HistoryFilter, Platform


class HistoryService:
    def __init__(self, db_path: Path | None = None) -> None:
        base = Path(db_path) if db_path else Path(user_data_dir("multi_downloader", appauthor=False))
        base.mkdir(parents=True, exist_ok=True)
        self._db = base / "history.sqlite"
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    output_path TEXT,
                    status TEXT NOT NULL,
                    error_message TEXT
                )
                """
            )

    def add_entry(
        self,
        *,
        platform: Platform | str,
        url: str,
        title: str | None,
        output_path: str | None,
        status: str,
        error_message: str | None = None,
    ) -> int:
        platform_enum = platform if isinstance(platform, Platform) else Platform(platform)
        created = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO history (created_at, platform, url, title, output_path, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created,
                    platform_enum.value,
                    url,
                    title,
                    output_path,
                    status,
                    error_message,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_entries(self, filt: HistoryFilter | None = None) -> list[HistoryEntry]:
        filt = filt or HistoryFilter()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, platform, url, title, output_path, status, error_message
                FROM history
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                (filt.limit, filt.offset),
            ).fetchall()
        out: list[HistoryEntry] = []
        for r in rows:
            ts = str(r["created_at"])
            if ts.endswith("Z"):
                ts = ts[:-1] + "+00:00"
            created_at = datetime.fromisoformat(ts)
            out.append(
                HistoryEntry(
                    id=r["id"],
                    created_at=created_at,
                    platform=Platform(r["platform"]),
                    url=r["url"],
                    title=r["title"],
                    output_path=r["output_path"],
                    status=r["status"],
                    error_message=r["error_message"],
                )
            )
        return out

    def clear(self) -> None:
        """Delete all history entries."""
        with self._connect() as conn:
            conn.execute("DELETE FROM history")
            conn.commit()
