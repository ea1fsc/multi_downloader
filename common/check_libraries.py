# This script checks if the necessary libraries are installed to run youtube_downloader.


import importlib
import subprocess
import sys


def check_and_install_libraries(libraries):
    for library in libraries:
        try:
            # Check if the library is installed
            importlib.import_module(library)
            print(
                f"The library '{library}' is installed. Requirements are met satisfactorily."
            )
        except ImportError:
            # If the library is not installed, prompt the user for installation
            print(f"The library '{library}' is not installed.")
            user_input = (
                input(f"Would you like to install '{library}'? (yes/no): ")
                .strip()
                .lower()
            )
            if user_input in ["yes", "y"]:
                try:
                    # Attempt to install the library using pip
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", library]
                    )
                    print(f"The library '{library}' has been installed successfully.")
                except subprocess.CalledProcessError:
                    print(
                        f"Failed to install '{library}'. Please try to install it manually."
                    )
            else:
                print(
                    f"You chose not to install '{library}'. You will need to install it manually."
                )

def main():
    check_and_install_libraries(libraries)
# List of libraries to check
libraries = ["pytubefix", "requests", "instaloader"]

if __name__ == "__main__":
    main()