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

# System libraries the bundled Qt needs for `--gui`. PyInstaller never bundles
# libGL/libEGL, libxcb or libwayland, and the others are bundled only when present
# on the build machine. The terminal mode works without them, so they are
# Recommends (installed by default by apt) / optdepends rather than hard deps.
DEB_GUI_RECOMMENDS = (
    "libgl1",
    "libegl1",
    "libxcb1",
    "libx11-xcb1",
    "libxcb-cursor0",
    "libxcb-icccm4",
    "libxcb-image0",
    "libxcb-keysyms1",
    "libxcb-randr0",
    "libxcb-render-util0",
    "libxcb-shape0",
    "libxcb-xkb1",
    "libxkbcommon0",
    "libxkbcommon-x11-0",
    "libfontconfig1",
    "libdbus-1-3",
    "libwayland-client0",
    "libwayland-cursor0",
    "libglib2.0-0t64 | libglib2.0-0",  # renamed in the 64-bit time_t transition
)
ARCH_GUI_OPTDEPENDS = (
    "libglvnd",
    "libxcb",
    "xcb-util-cursor",
    "xcb-util-wm",
    "xcb-util-image",
    "xcb-util-keysyms",
    "xcb-util-renderutil",
    "libxkbcommon",
    "libxkbcommon-x11",
    "fontconfig",
    "dbus",
    "wayland",
    "glib2",
)

CONTROL_TEMPLATE = """Package: multi-downloader
Version: {version}
Section: utils
Priority: optional
Architecture: {deb_arch}
Maintainer: ea1fsc <ea1fsc@users.noreply.github.com>
Homepage: https://github.com/ea1fsc/multi_downloader
Depends: libc6
Recommends: {recommends}
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
{optdepends}"""


def detect_arches() -> tuple[str, str]:
    machine = os.uname().machine
    if machine in {"x86_64", "amd64"}:
        return "amd64", "x86_64"
    if machine in {"aarch64", "arm64"}:
        return "arm64", "aarch64"
    raise SystemExit(f"Unsupported architecture: {machine}")


def _chmod_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _root_owned(info: tarfile.TarInfo) -> tarfile.TarInfo:
    """Ship files as root:root, never as the build user (pacman keeps archive ownership)."""
    info.uid = info.gid = 0
    info.uname = info.gname = "root"
    return info


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
            CONTROL_TEMPLATE.format(
                version=version, deb_arch=deb_arch, recommends=", ".join(DEB_GUI_RECOMMENDS)
            ),
            encoding="utf-8",
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Without --root-owner-group the files keep the build user's uid/gid (dpkg >= 1.19).
        subprocess.run([dpkg, "--root-owner-group", "--build", str(root), str(dest)], check=True)
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
                optdepends="".join(f"optdepend = {pkg}: desktop GUI (--gui)\n" for pkg in ARCH_GUI_OPTDEPENDS),
            ),
            encoding="utf-8",
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(dest, "w:xz") as tar:
            tar.add(root / ".PKGINFO", arcname=".PKGINFO", filter=_root_owned)
            tar.add(target, arcname="usr/bin/multi-downloader", filter=_root_owned)
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
