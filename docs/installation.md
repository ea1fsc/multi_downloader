# Installation

Run from a clone of this repository. There is no Docker image and no published package on PyPI that this project maintains.

**Requirements**

- Python **3.12 or newer** (`.python-version` pins `3.12.4`)
- `pip` and a virtual environment
- Network when you install packages and when you download media

## 1. Get the source

```bash
git clone https://github.com/ea1fsc/multi_downloader.git
cd multi_downloader
```

If you already have a copy, `cd` into that directory instead.

## 2. Create a virtualenv

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

`python` must be 3.12+. On some systems the binary is `python3`.

## 3. Install dependencies

From the repository root:

```bash
pip install -r requirements.txt
```

That file currently installs: `instaloader`, `pytubefix`, `requests`, `yt-dlp`, and `pytest`.

Editable install from `pyproject.toml` (same runtime libraries; pytest is extra `dev`):

```bash
pip install -e .
pip install -e ".[dev]"    # pytest, if you did not use requirements.txt
```

`pyproject.toml` lists version `0.1.0`; tagged releases in git and the root `CHANGELOG.md` are the product versions (current: v0.3).

## 4. Check libraries (optional)

```bash
python common/check_libraries.py
```

This imports `pytubefix`, `requests`, `instaloader`, and `yt_dlp`. Missing packages get a hint to re-run `pip install -r requirements.txt`.

## 5. Run

```bash
python multi_downloader.py
```

Platform modules can also be started directly (see [Usage](usage.md)).

## Tests (optional)

```bash
pytest
```

`pytest.ini` sets `testpaths = tests` and `pythonpath = .`. Tests do not download live media.

## Upgrading

```bash
git pull
source .venv/bin/activate
pip install -r requirements.txt
```

Re-run `python common/check_libraries.py` if a platform library started failing after an upgrade.

## Uninstall

Deactivate the venv and delete the clone (and `.venv` if you created it inside the repo). Downloaded media stays in the folder you chose; the program does not uninstall those files.
