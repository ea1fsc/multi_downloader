# multi_downloader
The objective of this repository is to create a multi-platform media downloader (supporting Instagram, YouTube, Twitter, and more), so you won't need to rely on third-party websites with uncertain operations. This tool will be available for any OS and will support different languages (for example, to find the Downloads path).

## DISCLAIMER
Currently, this project is maintained by a single person, so updates and feature implementations may not be rapid (I apologize for that :|). However, any contributions, whether as a tester, by providing feedback, coding, or simply reporting issues or suggesting future features, would be greatly appreciated.

S## Features:
- Instagram Downloader: this script allows you to download posts from Instagram, including photos, videos, and reels. If the account is private, you may need to log in (this functionality is not yet developed). You can also choose where to save the file and give it a custom name.

- Twitter Downloader: this script allows you to download videos from Twitter (note that downloading photos is not supported because it is integrated into the Twitter app). This feature is not yet developed. You will be able to choose where to save the file and give it a custom name.

- YouTube Downloader: this script allows you to download content from YouTube in three different formats: video, audio, or both (progressive). You can select from all the available streams on YouTube. Additionally, you can choose where to save the file and give it a custom name.

## How to Run the Program

To execute the program, follow these steps:

1. Run the `check_libraries.py` file inside the `common` folder to verify that all dependencies are met and, if necessary, install any missing libraries:
   `python common/check_libraries.py`
2. Run the `multi_downloader.py` file from the root directory:
    `python multi_downloader.py`
If you want to run a single module instead of the entire program, you can do so by executing the specific module with:
    `python x/x_downloader.py`
where `x` is the source (Instagram, YouTube, etc.). For example, to run only the YouTube downloader:
    `python YouTube/youtube_downloader.py`