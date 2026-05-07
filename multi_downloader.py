# This file contains the main code to run all the media downloader features
# Author: Juanchi (ea1fsc)
# Contributors:

import argparse
import os

from common import variables as vr
from Instagram import instagram_downloader as ind
from Twitter import twitter_downloader as twd
from YouTube import youtube_downloader as ytd


def parse_args() -> argparse.Namespace:
    """Parse optional non-interactive CLI arguments."""
    parser = argparse.ArgumentParser(description="Multi-platform media downloader")
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
    return parser.parse_args()


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


if __name__ == "__main__":
    try:
        args = parse_args()
        if args.platform:
            raise SystemExit(run_non_interactive(args))

        print(vr.banner)
        print(vr.banner_title)
        print("Welcome to the Media Downloader!")
        print("Press CTRL + C when you want to exit the program.")
        exits = False
        while not exits:
            print("-" * 41)
            sel = input(
                f"""Select an option:
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
                else:
                    print("An error has occurred. Please try again.")
            elif sel == "2":
                if twd.main() == 0:
                    continue
                else:
                    print("An error has occurred. Please try again.")
            elif sel == "3":
                if ytd.main() == 0:
                    continue
                else:
                    print("An error has occurred. Please try again.")
            else:
                print("Invalid option. Please choose one from the list.")

        print("-" * 41)
        print("Thanks for using the Multi-Downloader!! :D")
        exit(0)

    except KeyboardInterrupt:
        print("\n" + ("-" * 41))
        print("Thanks for using the Multi-Downloader!! :D")
        exit(0)
