import importlib
from __future__ import annotations


LIBRARIES = {
    "pytubefix": "pytubefix",
    "requests": "requests",
    "instaloader": "instaloader",
    "yt-dlp": "yt_dlp",
}


def check_libraries(libraries: dict[str, str]) -> bool:
    """Check required modules and print install hints when missing."""
    missing: list[str] = []
    for package_name, import_name in libraries.items():
        try:
            importlib.import_module(import_name)
            print(f"'{package_name}' is installed.")
        except ImportError:
            missing.append(package_name)

    if not missing:
        print("All dependencies are available.")
        return True

    print("Missing dependencies detected:")
    for package_name in missing:
        print(f"- {package_name}")
    print("Install them with: pip install -r requirements.txt")
    return False


def main() -> int:
    """Run dependency diagnostics only."""
    print("Checking required libraries...")
    return 0 if check_libraries(LIBRARIES) else 1

if __name__ == "__main__":
    raise SystemExit(main())