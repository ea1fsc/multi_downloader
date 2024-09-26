# This file contains common functions used by different scripts

# Needed libraries import
import os
import platform
import requests


def check_url_accessibility(url):
    """
    This function checks if the provided URL is accessible on the internet.
    Args:
        url (str): The URL to be checked.
    Returns:
        bool: True if the URL is accessible (status code 200), False otherwise.
    """
    try:
        response = requests.get(url)  # Send a GET request to the URL
        if response.status_code == 200:  # Check if the status code is 200 (OK)
            return True
        else:
            print(
                f"URL returned status code {response.status_code}."
            )  # Print status code if not 200
            return False
    except requests.RequestException as e:  # Handle any request exceptions
        print(f"An error occurred: {e}")  # Print the error message
        return False


def get_valid_download_directory():
	"""
	Asks the user for a download directory. If none is provided, uses the default Downloads/Descargas folder based on the operating system and language.
	Checks if the directory exists and is writable.
	
	Returns:
		str: The valid directory path where the file should be downloaded.
	"""
	while True:
		# Ask the user to specify a directory or press Enter for default
		download_dir = input("Enter the directory where you want to save the file (press Enter for default Downloads folder): ").strip()

		# If no directory is provided, use the default Downloads folder
		if not download_dir:
			system_name = platform.system()
			home_dir = os.path.expanduser("~")  # Get user's home directory

			if system_name == "Windows" or system_name == "Darwin":  # macOS and Windows
				# Check both "Downloads" and "Descargas" for Windows/macOS
				download_dir = os.path.join(home_dir, "Downloads")
				if not os.path.exists(download_dir):  # Fallback to "Descargas"
					download_dir = os.path.join(home_dir, "Descargas")

			elif system_name == "Linux":
				# Check both "Descargas" and "Downloads" for Linux
				download_dir = os.path.join(home_dir, "Descargas")
				if not os.path.exists(download_dir):  # Fallback to "Downloads"
					download_dir = os.path.join(home_dir, "Downloads")
			else:
				print("Unsupported OS. Please specify the directory manually.")
				continue

		# Validate if the directory exists
		if os.path.isdir(download_dir):
			# Check if the directory is writable
			if os.access(download_dir, os.W_OK):
				return download_dir
			else:
				print(f"The directory '{download_dir}' is not writable. Please choose a different directory.")
		else:
			print(f"Invalid directory: '{download_dir}'. Please enter a valid path.")