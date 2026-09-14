"""Extract a CHANGELOG.md section for a git tag (v0.3, v1.2.3, ...)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^## \[([^\]]+)\][^\n]*\n", re.MULTILINE)


def _normalize(label: str) -> str:
    text = label.strip()
    if text.lower().startswith("v"):
        text = text[1:]
    return text


def extract_section(changelog: str, version: str) -> str | None:
    wanted = _normalize(version)
    headings = list(HEADING.finditer(changelog))
    for index, match in enumerate(headings):
        if _normalize(match.group(1)) != wanted:
            continue
        start = match.start()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(changelog)
        return changelog[start:end].strip()
    return None


def extract_unreleased(changelog: str) -> str | None:
    headings = list(HEADING.finditer(changelog))
    for index, match in enumerate(headings):
        if match.group(1).strip().lower() != "unreleased":
            continue
        start = match.start()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(changelog)
        return changelog[start:end].strip()
    return None


def notes_for_tag(changelog: str, tag: str) -> str:
    section = extract_section(changelog, tag)
    if section:
        return section
    fallback = extract_unreleased(changelog)
    if fallback:
        return fallback
    return f"Release {tag}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print CHANGELOG notes for a version tag.")
    parser.add_argument("tag", help="Git tag, for example v0.4 or v1.2.3.")
    parser.add_argument(
        "--changelog",
        type=Path,
        default=Path("CHANGELOG.md"),
        help="Path to CHANGELOG.md.",
    )
    args = parser.parse_args(argv)
    text = args.changelog.read_text(encoding="utf-8")
    print(notes_for_tag(text, args.tag))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
