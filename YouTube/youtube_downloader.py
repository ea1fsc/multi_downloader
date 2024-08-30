# This script allows you to search for a video in YouTube, get it features, and select if you want to download the audio, the video or all togheter in different formats and qualities.
# Author: Juanchi (ea1fsc)
# Contributors:

# Library imports
import datetime
import pytubefix as pyt
import os
import platform
import re
import sys

# Local imports
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "common"))
)
import variables as vr
import functions as func

# Define global variables for the YouTube object
yt = None
banner_yt = vr.banner_yt
separator = vr.separator


# Deffinition of functions used by the script
def request_url():
    """This functions returns the url once it is validated
    thtat the URL provided is a YouTube one.
    Args: none
    Returns: url. URL of the video."""

    # Regular expression to validate YouTube URLs
    youtube_regex = (
        r"(https?://)?(www\.)?youtube\.com/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
    )
    print(separator)
    while True:
        url = input("Please, enter the YouTube video URL: ").strip()

        # Check if the URL is not empty and matches the YouTube regex
        if url and re.match(youtube_regex, url):
            return url
        else:
            print("Please enter a valid YouTube URL.")


def display_video_info(url):
    """
    This function creates a YouTube object from the given URL and displays its details.
    Args:
        url (str): The YouTube video URL.
    Returns:
        bool: True if the user confirms the video with 'y', False if the user declines with 'n'.
    """
    global yt
    try:
        yt = pyt.YouTube(url)  # Create a global YouTube object
        title = yt.title  # Get the video title
        duration = str(
            datetime.timedelta(seconds=yt.length)
        )  # Get video duration in hh:mm:ss
        channel_title = yt.author  # Get the channel name
        channel_url = yt.channel_url  # Get the channel URL

        # Display video details
        print(separator)
        print(f"Title: {title}")
        print(f"Duration: {duration}")
        print(f"Channel: {channel_title}")
        print(f"Channel URL: {channel_url}")
        print(separator)

        while True:
            # Ask user to confirm if this is the desired video
            user_response = input("Is this the video you want? (y/n): ").strip().lower()
            if user_response == "y":  # If user confirms
                print(separator)
                return True
            elif user_response == "n":  # If user declines
                return False
            else:
                print(
                    "Invalid input. Please enter 'y' or 'n'."
                )  # Prompt user for valid input

    except Exception as e:
        print(f"An error occurred while fetching video details: {e}")
        return False


def get_streams_by_format(yt_video, format_choice):
    """
    Retrieves all streams for a given YouTube video based on the selected format.

    Args:
        yt_video (YouTube): The YouTube object for the video.
        format_choice (str): The selected format ('audio', 'video', 'audio+video').

    Returns:
        list: A list of streams that match the selected format.
    """
    # Fetch all available streams from the video
    streams = yt_video.streams

    if format_choice == "audio":
        # Filter for audio-only streams
        return streams.filter(only_audio=True)

    elif format_choice == "video":
        # Filter for video-only streams (excluding progressive streams)
        return streams.filter(only_video=True, progressive=False)

    elif format_choice == "audio+video":
        # Filter for progressive streams (contain both audio and video)
        return streams.filter(progressive=True)


def display_stream_info(i, stream, format_choice):
    """
    This function displays information about each stream in the provided list of streams.
    Args:
        i: Index of the stream
        stream: Stream from a YouTube video.
        format_choice: Type of stream.
    """

    # Get file format (e.g., mp4, webm)
    file_format = stream.mime_type.split("/")[-1] if stream.mime_type else "Unknown"

    # Get codec
    codec = stream.codecs[0] if stream.codecs else "Unknown"

    # Get resolution (if available)
    resolution = stream.resolution if stream.resolution else "N/A"

    # Print stream information
    print(
        f"[{i}] Type: {format_choice} | Format: {file_format} | Codec: {codec} | Resolution: {resolution}"
    )


def confirm_stream(streams):
    print(separator)
    while True:
        selected = input("Select the desired file: ")
        if selected.isdigit():
            index = int(selected)
            try:
                stream = streams[index - 1]
                display_stream_info(index, stream, "video")
                while True:
                    ans = (
                        input("Please confirm if it is the correct stream (y/n): ")
                        .strip()
                        .lower()
                    )
                    print(separator)
                    if ans == "y":
                        return True, index, stream
                    else:
                        return False, None, None
            except IndexError as e:
                print("The selected stream does not exist. Select another one.")
        else:
            print("Answer not valid. Please choose one option from the list")


def download_stream(stream):
    """
    This function downloads the specified stream after asking the user for the download directory and file name.
    Args:
        stream (Stream): The YouTube stream to be downloaded.
    """
    # Step 1: Ask for the download directory
    while True:
        download_dir = input(
            "Enter the directory where you want to save the file (press Enter for default Downloads folder): "
        ).strip()
        if not download_dir:
            # Determine the default downloads folder based on the operating system
            system_name = platform.system()
            if system_name == "Windows":
                download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            elif system_name == "Darwin":  # macOS
                download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            elif system_name == "Linux":
                download_dir = os.path.join(os.path.expanduser("~"), "Descargas")
                if not os.path.exists(
                    download_dir
                ):  # In case it's not in Spanish, fall back to "Downloads"
                    download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            else:
                print("Unsupported OS. Please specify the directory manually.")
                continue
        if os.path.isdir(download_dir):
            break
        else:
            print("Invalid directory. Please enter a valid path.")

    # Step 2: Ask for the file name
    file_name = input("Enter the file name (press Enter for the video title): ").strip()
    if not file_name:
        file_name = stream.title  # Use the title of the video as the file name

    # Ensure the file name has the correct extension
    file_extension = stream.mime_type.split("/")[
        -1
    ]  # Get the file extension from the stream's MIME type
    if not file_name.endswith(f".{file_extension}"):
        file_name = f"{file_name}.{file_extension}"

    # Download the stream to the specified directory with the given file name
    try:
        print(f"Downloading to: {os.path.join(download_dir, file_name)}")
        stream.download(output_path=download_dir, filename=file_name)
        print("Download completed successfully.")
    except Exception as e:
        print(f"An error occurred during the download: {e}")


def main():
    """
    This function runs the process to download from YouTube.
    Returns:
        int 0: this means all the process was right (like exit(0) but without stoping)
    """
    access = False
    confirm = False
    mode = False
    mode2 = False
    print(banner_yt)
    print("Welcome to the YouTube Downloader!")
    while True:
        while not (access) or not (confirm):
            url = request_url()
            access = func.check_url_accessibility(url)
            confirm = display_video_info(url)
        sel = input(
            f"""Select the option you desire:
1 - Download a video (without audio).
2 - Download an audio.
3 - Download video (with audio).
0 - Select another URL.
Selected option: """
        )
        if sel == "1":
            print(separator)
            print("Listing all the video posibilities...\n")
            streams = get_streams_by_format(yt, "video")
            while not mode:
                for i, stream in enumerate(streams, start=1):
                    display_stream_info(i, stream, "video")
                mode, index, stream = confirm_stream(streams)
            download_stream(stream)
            while not mode2:
                other = input("Do you want to download another file? (y/n):")
                if other == "y":
                    other2 = input("From the same URL? (y/n):")
                    if other2 == "y":
                        mode = False
                        break
                    elif other2 == "n":
                        access = False
                        confirm = False
                        break
                    else:
                        print("Answer not valid")
                elif other == "n":
                    print(
                        "Thanks for using YouTube Downloader. Going back to the main menu..."
                    )
                    return 0
                else:
                    print("Answer not valid.")
        elif sel == "2":
            print(separator)
            print("Listing all the audio posibilities...\n")
            streams = get_streams_by_format(yt, "audio")
            while not mode:
                for i, stream in enumerate(streams, start=1):
                    display_stream_info(i, stream, "video")
                mode, index, stream = confirm_stream(streams)
            download_stream(stream)
            while not mode2:
                other = input("Do you want to download another file? (y/n):")
                if other == "y":
                    other2 = input("From the same URL? (y/n):")
                    if other2 == "y":
                        mode = False
                        break
                    elif other2 == "n":
                        access = False
                        confirm = False
                        break
                    else:
                        print("Answer not valid")
                elif other == "n":
                    print(
                        "Thanks for using YouTube Downloader. Going back to the main menu..."
                    )
                    return 0
                else:
                    print("Answer not valid.")
        elif sel == "3":
            print(separator)
            print("Listing all the video (with audio) posibilities...\n")
            streams = get_streams_by_format(yt, "audio+video")
            while not mode:
                for i, stream in enumerate(streams, start=1):
                    display_stream_info(i, stream, "audio+video")
                mode, index, stream = confirm_stream(streams)
            download_stream(stream)
            while not mode2:
                other = input("Do you want to download another file? (y/n):")
                if other == "y":
                    other2 = input("From the same URL? (y/n):")
                    if other2 == "y":
                        mode = False
                        break
                    elif other2 == "n":
                        access = False
                        confirm = False
                        break
                    else:
                        print("Answer not valid")
                elif other == "n":
                    print(
                        "Thanks for using YouTube Downloader. Going back to the main menu..."
                    )
                    return 0
                else:
                    print("Answer not valid.")
        elif sel == "0":
            access = False
            confirm = False
        else:
            print("Choose a valid option please.")


if __name__ == "__main__":
    main()
