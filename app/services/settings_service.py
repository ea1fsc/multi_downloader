"""Persistent application settings (JSON, schema-versioned)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir

from app.domain.models import AppSettings


class SettingsService:
    def __init__(self, config_dir: Path | None = None) -> None:
        base = Path(config_dir) if config_dir else Path(user_config_dir("multi_downloader", appauthor=False))
        base.mkdir(parents=True, exist_ok=True)
        self._path = base / "settings.json"

    def load(self) -> AppSettings:
        if not self._path.is_file():
            return AppSettings()
        try:
            raw: dict[str, Any] = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return AppSettings()
        schema = int(raw.get("schema_version", 1))
        if schema != 1:
            return AppSettings()
        return AppSettings(
            schema_version=schema,
            default_download_dir=raw.get("default_download_dir"),
            collision_policy=str(raw.get("collision_policy", "rename")),
        )

    def save(self, settings: AppSettings) -> None:
        payload = {
            "schema_version": settings.schema_version,
            "default_download_dir": settings.default_download_dir,
            "collision_policy": settings.collision_policy,
        }
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
