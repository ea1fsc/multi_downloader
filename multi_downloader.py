# This file contains the main code to run all the media downloader features
# Author: Juanchi (ea1fsc)
# Contributors:

# Imports
import sys
import os
from common import variables as vr
from Instagram import instagram_downloader as ind
from Twitter import twitter_downloader as twd
from YouTube import youtube_downloader as ytd


if __name__ == "__main__":
    try:
        print(vr.banner)
        print("Welcome to the Media Downloader!")
        print("Press CTRL + c (Control + c) when you want to exist the program")
        exits = False
        while not exits:
            print(vr.separator)
            sel = input(
                f"""Select the option you desire:
1 - Download from Instagram.
2 - Download from Twitter.
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
                    print("An error has ocurred! Please try again.")
            elif sel == "2":
                if twd.main() == 0:
                    continue
                else:
                    print("An error has ocurred! Please try again.")
            elif sel == "3":
                if ytd.main() == 0:
                    continue
                else:
                    print("An error has ocurred! Please try again.")
            else:
                print("Option not valid. Please, choose one from the list.")

        print(vr.separator)
        print("Thanks for using the Multi-Downloader!! :D")
        exit(0)

    except KeyboardInterrupt:
        print("\n" + vr.separator)
        print("Thanks for using the Multi-Downloader!! :D")
        exit(0)
