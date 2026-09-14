"""Wrap the Linux PyInstaller binary as .deb and Arch pkg.tar.xz."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

CONTROL_TEMPLATE = """Package: multi-downloader
Version: {version}
Section: utils
Priority: optional
Architecture: {deb_arch}
Maintainer: ea1fsc <ea1fsc@users.noreply.github.com>
Homepage: https://github.com/ea1fsc/multi_downloader
Depends: libc6
Description: Multi-platform media downloader (CLI and GUI)
 Local downloader for Instagram, Twitter/X, and YouTube.
 Supports a terminal interface and a desktop GUI (`--gui`).
"""

PKGINFO_TEMPLATE = """pkgname = multi-downloader
pkgver = {version}-1
pkgdesc = Multi-platform media downloader (CLI and GUI)
url = https://github.com/ea1fsc/multi_downloader
builddate = {builddate}
packager = GitHub Actions
size = {size}
arch = {arch_arch}
license = GPL-3.0-or-later
depend = glibc
"""


def detect_arches() -> tuple[str, str]:
    machine = os.uname().machine
    if machine in {"x86_64", "amd64"}:
        return "amd64", "x86_64"
    if machine in {"aarch64", "arm64"}:
        return "arm64", "aarch64"
    raise SystemExit(f"Unsupported architecture: {machine}")


def _chmod_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def build_deb(binary: Path, version: str, dest: Path, deb_arch: str) -> Path:
    dpkg = shutil.which("dpkg-deb")
    if not dpkg:
        raise SystemExit("dpkg-deb is required to build the Debian package (install dpkg-dev).")

    with tempfile.TemporaryDirectory(prefix="multi-downloader-deb-") as tmp:
        root = Path(tmp)
        bindir = root / "usr" / "bin"
        debian = root / "DEBIAN"
        bindir.mkdir(parents=True)
        debian.mkdir()
        target = bindir / "multi-downloader"
        shutil.copy2(binary, target)
        _chmod_executable(target)
        (debian / "control").write_text(
            CONTROL_TEMPLATE.format(version=version, deb_arch=deb_arch),
            encoding="utf-8",
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([dpkg, "--build", str(root), str(dest)], check=True)
    return dest


def build_arch_pkg(binary: Path, version: str, dest: Path, arch_arch: str) -> Path:
    with tempfile.TemporaryDirectory(prefix="multi-downloader-arch-") as tmp:
        root = Path(tmp)
        bindir = root / "usr" / "bin"
        bindir.mkdir(parents=True)
        target = bindir / "multi-downloader"
        shutil.copy2(binary, target)
        _chmod_executable(target)
        size = target.stat().st_size
        (root / ".PKGINFO").write_text(
            PKGINFO_TEMPLATE.format(
                version=version,
                builddate=int(time.time()),
                size=size,
                arch_arch=arch_arch,
            ),
            encoding="utf-8",
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(dest, "w:xz") as tar:
            tar.add(root / ".PKGINFO", arcname=".PKGINFO")
            tar.add(target, arcname="usr/bin/multi-downloader")
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create Debian and Arch packages from the Linux binary.")
    parser.add_argument("--binary", type=Path, required=True, help="Path to the Linux PyInstaller binary.")
    parser.add_argument("--version", required=True, help="Package version without a leading v (for example 0.4).")
    parser.add_argument("--output-dir", type=Path, default=Path("dist"), help="Directory for generated packages.")
    args = parser.parse_args(argv)

    binary = args.binary.resolve()
    if not binary.is_file():
        print(f"Binary not found: {binary}", file=sys.stderr)
        return 1

    deb_arch, arch_arch = detect_arches()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)

    deb_path = output / f"multi-downloader_{args.version}_{deb_arch}.deb"
    arch_path = output / f"multi-downloader-{args.version}-1-{arch_arch}.pkg.tar.xz"

    build_deb(binary, args.version, deb_path, deb_arch)
    build_arch_pkg(binary, args.version, arch_path, arch_arch)
    print(f"Wrote {deb_path}")
    print(f"Wrote {arch_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
