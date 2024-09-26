# This script allows you to dowload posts from Instagram.
# Author: Juanchi (ea1fsc)
# Contributors:

# Libraries imports
import os
import re
import sys
import instaloader
#import pathlib

# Local imports
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "common"))
)
import variables as vr
import functions as func

#Variables
banner_instagram = vr.banner_instagram
separator = vr.separator

#Functions used
def get_instagram_url() -> str:
	"""
	Prompts the user to enter a URL and checks if it is a valid Instagram URL.
	Ensures that the input is not empty.

	Returns:
		str: The valid Instagram URL entered by the user.
	"""
	while True:
		url = input("Please enter the Instagram URL: ").strip()
		
		# Check if the input is empty
		if not url:
			print("The URL cannot be empty. Please enter a valid Instagram URL.")
			continue
		
		# Regular expression to match Instagram URLs
		instagram_url_pattern = r'^https?://(www\.)?instagram\.com/.+'
		
		if re.match(instagram_url_pattern, url):
			return url
		else:
			print("Invalid Instagram URL. Please try again.")


import os
import instaloader

def download_instagram_post(url):
	"""
	Downloads an Instagram post (either video or image) after asking the user for the download directory 
	and file name.
	Args:
		url (str): The URL of the desired Instagram post
	"""
	# Step 1: Initialize Instaloader
	loader = instaloader.Instaloader(save_metadata=False, download_comments=False)
	
	# Step 2: Extract the shortcode from the URL
	shortcode = url.split("/")[-2]
	
	try:
		# Fetch post using shortcode
		post = instaloader.Post.from_shortcode(loader.context, shortcode)

		# Step 3: Ask for the download directory
		download_dir = func.get_valid_download_directory()

		# Step 4: Ask for the file name
		file_name = input("Enter the file name (press Enter for default name): ").strip()
		if not file_name:
			file_name = shortcode  # Use the shortcode as the default file name

		if post.is_video:
			file_name += '.mp4'
		else:
			file_name += '.jpg'

		full_path = os.path.join(download_dir, f"{file_name}")
		print(full_path)
		if os.path.exists(full_path):
			base, extension = os.path.splitext(full_path)
			print(extension)
			counter = 1
			while os.path.exists(f"{base}_{counter}{extension}"):
				counter += 1
			full_path = f"{base}_{counter}"
		else:
			full_path = full_path[:-4]
		print(full_path)
		if post.is_video:
			try:
				loader.download_pic(filename=full_path, url=post.video_url, mtime=post.date_local)
			except:
				print(f'An error occurred during the download: {e}')
		else:
			try:
				loader.download_pic(filename=full_path, url=post.url, mtime=post.date_local)
			except:
				print(f'An error occurred during the download: {e}')

	except Exception as e:
		print(f'The Instagram post is not reachable. Reason: {e}')

# Is not being developed yet
def main():
	access = False
	print(banner_instagram)
	print("Welcome to the Instagram Downloader")
	print(separator)
	while not access:
		url = get_instagram_url()
		access = func.check_url_accessibility(url)
	download_instagram_post(url)
	return 0


if __name__ == "__main__":
    main()
