"""Tests for release changelog extraction (load by path; avoid stdlib 'packaging')."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_extract():
    path = ROOT / "packaging" / "extract_changelog.py"
    spec = importlib.util.spec_from_file_location("extract_changelog", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SAMPLE = """# Changelog

## [Unreleased]

### Added
- New GUI flag.

## [v0.3] - 2026-05-07

### Added
- Twitter downloader.

## [v0.2] - 2024-09-26

### Added
- Instagram.
"""


def test_extract_section_for_v0_3() -> None:
    extract = _load_extract()
    notes = extract.notes_for_tag(SAMPLE, "v0.3")
    assert "Twitter downloader" in notes
    assert "New GUI flag" not in notes
    assert "Instagram" not in notes


def test_extract_falls_back_to_unreleased() -> None:
    extract = _load_extract()
    notes = extract.notes_for_tag(SAMPLE, "v9.9")
    assert "New GUI flag" in notes


def test_extract_real_changelog_v0_3() -> None:
    extract = _load_extract()
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    notes = extract.notes_for_tag(text, "v0.3")
    assert "Twitter/X downloader module" in notes
