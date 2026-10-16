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


def _load_packager():
    path = ROOT / "packaging" / "make_linux_packages.py"
    spec = importlib.util.spec_from_file_location("make_linux_packages", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_arch_package_files_are_owned_by_root(tmp_path) -> None:
    import tarfile

    packager = _load_packager()
    binary = tmp_path / "bin"
    binary.write_bytes(b"#!/bin/sh\n")
    dest = packager.build_arch_pkg(binary, "1.0", tmp_path / "pkg.tar.xz", "x86_64")
    with tarfile.open(dest) as tar:
        members = tar.getmembers()
    assert {m.name for m in members} == {".PKGINFO", "usr/bin/multi-downloader"}
    for member in members:
        assert (member.uid, member.gid, member.uname, member.gname) == (0, 0, "root", "root")
    binary_member = next(m for m in members if m.name == "usr/bin/multi-downloader")
    assert binary_member.mode & 0o111


def test_deb_build_requests_root_ownership(tmp_path, monkeypatch) -> None:
    packager = _load_packager()
    calls: list[list[str]] = []
    monkeypatch.setattr(packager.shutil, "which", lambda _name: "/usr/bin/dpkg-deb")
    monkeypatch.setattr(packager.subprocess, "run", lambda cmd, check: calls.append(cmd))
    binary = tmp_path / "bin"
    binary.write_bytes(b"#!/bin/sh\n")
    packager.build_deb(binary, "1.0", tmp_path / "pkg.deb", "amd64")
    assert calls and "--root-owner-group" in calls[0]
    assert calls[0].index("--root-owner-group") < calls[0].index("--build")


def test_arch_package_lists_gui_optdepends(tmp_path) -> None:
    import tarfile

    packager = _load_packager()
    binary = tmp_path / "bin"
    binary.write_bytes(b"#!/bin/sh\n")
    dest = packager.build_arch_pkg(binary, "1.0", tmp_path / "pkg.tar.xz", "x86_64")
    with tarfile.open(dest) as tar:
        pkginfo = tar.extractfile(".PKGINFO").read().decode()
    optdepends = [line.split(" = ", 1)[1].split(":")[0] for line in pkginfo.splitlines() if line.startswith("optdepend")]
    assert optdepends == list(packager.ARCH_GUI_OPTDEPENDS)
    assert "depend = glibc" in pkginfo.splitlines()


def test_deb_control_recommends_gui_libraries(tmp_path, monkeypatch) -> None:
    packager = _load_packager()
    controls: list[str] = []

    def fake_run(cmd, check):
        controls.append((Path(cmd[-2]) / "DEBIAN" / "control").read_text(encoding="utf-8"))

    monkeypatch.setattr(packager.shutil, "which", lambda _name: "/usr/bin/dpkg-deb")
    monkeypatch.setattr(packager.subprocess, "run", fake_run)
    binary = tmp_path / "bin"
    binary.write_bytes(b"#!/bin/sh\n")
    packager.build_deb(binary, "1.0", tmp_path / "pkg.deb", "amd64")
    fields = dict(line.split(": ", 1) for line in controls[0].splitlines() if ": " in line and not line.startswith(" "))
    assert fields["Depends"] == "libc6"
    assert fields["Recommends"].split(", ") == list(packager.DEB_GUI_RECOMMENDS)


def test_pkgbuild_optdepends_match_packager() -> None:
    import re

    packager = _load_packager()
    pkgbuild = (ROOT / "packaging" / "linux" / "PKGBUILD").read_text(encoding="utf-8")
    listed = re.findall(r"^\s+'([^:']+): desktop GUI", pkgbuild, re.MULTILINE)
    assert listed == list(packager.ARCH_GUI_OPTDEPENDS)
