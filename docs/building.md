# Building

Audience: anyone who wants a **standalone binary** (CLI and GUI in the same file) or a Linux package. You do not need this if you already run `python multi_downloader.py` from a clone.

The binary is named `multi-downloader` (`multi-downloader.exe` on Windows). It is **not** windowed: the same file runs the terminal UI by default and the Qt GUI with `--gui` / `-g`.

```bash
./multi-downloader
./multi-downloader --gui
./multi-downloader --platform youtube --url "https://youtu.be/dQw4w9WgXcQ" --mode audio --output "/tmp" --yes
```

GitHub Actions repeats these steps when you **push a tag** `vX`, `vX.Y`, or `vX.Y.Z` (for example `v0.4` or `v1.2.3`). The release notes are the matching section of `CHANGELOG.md`. GitHub also attaches source zip/tar for that tag.

## What you need on every OS

- Python **3.12 or newer**
- `pip` and a virtual environment
- Network, once, to install PyPI packages (including PySide6 and PyInstaller)
- A few hundred MB of disk: Qt is bundled into the binary

From the repository root:

```bash
python -m venv .venv
```

Then install GUI extras plus PyInstaller:

```bash
pip install -e ".[gui]" pyinstaller
python packaging/build.py
```

The file lands in `dist/multi-downloader` (or `dist/multi-downloader.exe` on Windows).

`packaging/build.py` uses `--onefile --console` so CLI output stays visible. Do not pass PyInstaller `--windowed` / `--noconsole`: that would hide the terminal mode.

If a Linux GUI build starts the CLI but `--gui` dies with a Qt “platform plugin” error, install OpenGL/X11 extras (`libgl1`, `libegl1`, `libxkbcommon0` on Debian; `mesa` and `libxkbcommon` on Arch) and rebuild.

## Windows

1. Install Python 3.12+ from [python.org](https://www.python.org/downloads/) and tick **Add python.exe to PATH**.
2. Open Command Prompt or PowerShell in the clone:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
pip install -e ".[gui]" pyinstaller
python packaging/build.py
```

3. Run `dist\multi-downloader.exe` or `dist\multi-downloader.exe --gui`.

No extra C compiler is required for this PyInstaller onefile build. Windows Defender may scan a freshly built `.exe` the first time you launch it.

## macOS

1. Install Python 3.12+ (Xcode command-line tools and/or Homebrew):

```bash
brew install python@3.12
```

2. From the clone:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[gui]" pyinstaller
python packaging/build.py
```

3. Run `dist/multi-downloader` or `dist/multi-downloader --gui`.

The binary is unsigned. Finder may block it until you allow it under **System Settings → Privacy & Security**, or you can run it from Terminal. GitHub Actions builds on Apple Silicon (`macos-arm64`).

## Linux (executable)

Works on Debian-based and Arch-based systems. Build the onefile binary first (section above), then run `dist/multi-downloader`.

### Debian, Ubuntu, and derivatives

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip python3-dev binutils dpkg-dev \
  libgl1 libegl1 libxkbcommon0 libdbus-1-3
```

Create the venv, install, and run `python packaging/build.py` as in the common steps. Optional Qt-related packages (`libgl1`, …) help PySide6 import while PyInstaller analyzes the project.

Then wrap the binary as a `.deb` (requires `dpkg-deb` from `dpkg-dev`):

```bash
python packaging/make_linux_packages.py \
  --binary dist/multi-downloader \
  --version 0.4 \
  --output-dir dist
sudo dpkg -i dist/multi-downloader_0.4_amd64.deb
```

Replace `0.4` with the version you are packaging. The helper also writes an Arch `pkg.tar.xz` next to the `.deb`; you can ignore that file on Debian.

### Arch Linux and derivatives

```bash
sudo pacman -S --needed python python-pip binutils fakeroot debugedit tar xz
```

Create the venv, install, and run `python packaging/build.py`. To install with `pacman`, either:

- Use the `pkg.tar.xz` from `packaging/make_linux_packages.py` (same command as on Debian; architecture is `x86_64` or `aarch64`), then `sudo pacman -U dist/multi-downloader-<version>-1-x86_64.pkg.tar.xz`, or
- Copy the binary next to the template and run `makepkg`:

```bash
cp dist/multi-downloader packaging/linux/multi-downloader
cd packaging/linux
PKGVER=0.4 makepkg -f
sudo pacman -U multi-downloader-0.4-1-x86_64.pkg.tar.zst
```

`packaging/linux/PKGBUILD` installs `/usr/bin/multi-downloader`. It packages the **prebuilt** binary; it does not re-run PyInstaller.

## After you have a binary

| Command | Mode |
| --- | --- |
| `multi-downloader` | Interactive CLI menu |
| `multi-downloader --gui` | Desktop GUI |
| `multi-downloader -g` | Same as `--gui` |
| `multi-downloader --platform …` | Non-interactive CLI (see [Usage](usage.md)) |

GUI settings and history still go to the per-user config/data directories described in [Configuration](configuration.md).

## Automated releases

Push an annotated or lightweight tag that matches `vX`, `vX.Y`, or `vX.Y.Z`:

```bash
git tag v0.4
git push origin v0.4
```

Workflow: `.github/workflows/release.yml`. It builds Windows, macOS, and Linux binaries, adds `.deb` and Arch `pkg.tar.xz`, and creates a GitHub Release whose body is the `CHANGELOG.md` section for that version (or `[Unreleased]` if that heading is missing). Source zip and tar.gz are attached by GitHub from the tag.

Put the version heading in `CHANGELOG.md` **before** tagging, for example `## [v0.4] - 2026-09-14`.
