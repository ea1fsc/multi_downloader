# This file contains common functions used by different scripts

# Needed libraries import
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
