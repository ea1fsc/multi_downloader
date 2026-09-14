"""Common helper functions shared across downloaders."""

from __future__ import annotations

import os
import platform
import re
from pathlib import Path
from typing import Callable

import requests


def check_url_accessibility(url: str, timeout: int = 10, *, quiet: bool = False) -> bool:
    """Check whether a URL is reachable."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True
        if not quiet:
            print(f"URL returned status code {response.status_code}.")
        return False
    except requests.RequestException as exc:
        if not quiet:
            print(f"An error occurred while checking URL accessibility: {exc}")
        return False


def sanitize_filename(name: str) -> str:
    """Return a filesystem-safe filename fragment."""
    return re.sub(r'[\\/*?:"<>|]+', "_", name).strip()


def ask_yes_no(prompt: str) -> bool:
    """Prompt until a valid yes/no answer is provided."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes", "n", "no"):
            return answer in ("y", "yes")
        print("Invalid input. Please type 'y/yes' or 'n/no'.")


def get_default_download_directory() -> str | None:
    """Return the best default download directory for the current OS."""
    home_dir = Path.home()
    system_name = platform.system()

    if system_name in ("Windows", "Darwin"):
        candidates = [home_dir / "Downloads", home_dir / "Descargas"]
    elif system_name == "Linux":
        candidates = [home_dir / "Descargas", home_dir / "Downloads"]
    else:
        return None

    for candidate in candidates:
        if candidate.is_dir():
            return str(candidate)
    return str(candidates[-1])


def get_valid_download_directory(
    input_fn: Callable[[str], str] = input,
) -> str:
    """
    Ask the user for a destination directory and validate it.

    If left empty, use a platform-specific default Downloads folder.
    """
    while True:
        download_dir = input_fn(
            "Enter the directory where you want to save the file "
            "(press Enter for default Downloads folder): "
        ).strip()

        if not download_dir:
            default_dir = get_default_download_directory()
            if default_dir is None:
                print("Unsupported OS. Please specify the directory manually.")
                continue
            download_dir = default_dir

        if os.path.isdir(download_dir):
            if os.access(download_dir, os.W_OK):
                return download_dir
            print(
                f"The directory '{download_dir}' is not writable. "
                "Please choose a different directory."
            )
            continue
        print(f"Invalid directory: '{download_dir}'. Please enter a valid path.")