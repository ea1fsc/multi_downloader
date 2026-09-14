# This file contains the main code to run all the media downloader features
# Author: Juanchi (ea1fsc)
# Contributors:

from __future__ import annotations

import argparse
import os
import sys

from common import variables as vr
from Instagram import instagram_downloader as ind
from Twitter import twitter_downloader as twd
from YouTube import youtube_downloader as ytd


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse optional CLI arguments, including desktop GUI mode."""
    parser = argparse.ArgumentParser(description="Multi-platform media downloader")
    parser.add_argument(
        "-g",
        "--gui",
        action="store_true",
        help="Launch the desktop GUI instead of the terminal interface.",
    )
    parser.add_argument(
        "--platform",
        choices=("instagram", "twitter", "youtube"),
        help="Run a single platform directly.",
    )
    parser.add_argument("--url", help="Direct media URL for non-interactive execution.")
    parser.add_argument("--output", help="Destination directory for the downloaded file.")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Assume yes for confirmations in non-interactive mode.",
    )
    parser.add_argument(
        "--mode",
        choices=("audio", "video", "audio+video"),
        help="YouTube mode when using --platform youtube.",
    )
    return parser.parse_args(argv)


def run_non_interactive(args: argparse.Namespace) -> int:
    """Run selected platform with CLI arguments."""
    if args.output and not os.path.isdir(args.output):
        print(f"Invalid output directory: {args.output}")
        return 1

    if args.platform == "instagram":
        return ind.main(
            preset_url=args.url,
            output_dir=args.output,
            assume_yes=args.yes,
        )
    if args.platform == "twitter":
        return twd.main(
            preset_url=args.url,
            output_dir=args.output,
            assume_yes=args.yes,
        )
    if args.platform == "youtube":
        return ytd.main(
            preset_url=args.url,
            output_dir=args.output,
            assume_yes=args.yes,
            preset_mode=args.mode,
        )
    print("Invalid platform value.")
    return 1


def _hide_windows_console() -> None:
    """Hide the extra console window when a frozen Windows GUI starts."""
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return
    try:
        import ctypes

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        return


def launch_gui() -> int:
    """Start the Qt desktop UI. Returns a process exit code."""
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print(
            "GUI dependencies are not installed.\n"
            "Install them with: pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    from ui.main_window import MainWindow

    _hide_windows_console()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return int(app.exec())


def run_interactive_menu() -> int:
    """Numbered terminal menu until the user exits."""
    print(vr.banner)
    print(vr.banner_title)
    print("Welcome to the Media Downloader!")
    print("Press CTRL + C when you want to exit the program.")
    exits = False
    while not exits:
        print("-" * 41)
        sel = input(
            """Select an option:
1 - Download from Instagram.
2 - Download from Twitter/X.
3 - Download from YouTube.
0 - Exit.
Selected option: """
        )
        if sel == "0":
            exits = True
        elif sel == "1":
            if ind.main() == 0:
                continue
            print("An error has occurred. Please try again.")
        elif sel == "2":
            if twd.main() == 0:
                continue
            print("An error has occurred. Please try again.")
        elif sel == "3":
            if ytd.main() == 0:
                continue
            print("An error has occurred. Please try again.")
        else:
            print("Invalid option. Please choose one from the list.")

    print("-" * 41)
    print("Thanks for using the Multi-Downloader!! :D")
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI menu, one-shot platform mode, or desktop GUI."""
    try:
        args = parse_args(argv)
        if args.gui:
            return launch_gui()
        if args.platform:
            return run_non_interactive(args)
        return run_interactive_menu()
    except KeyboardInterrupt:
        print("\n" + ("-" * 41))
        print("Thanks for using the Multi-Downloader!! :D")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
