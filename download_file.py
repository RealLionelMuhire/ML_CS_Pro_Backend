#!/usr/bin/env python
import os
from backend.helpers.firebase import download_file_from_url

def save_file(file_name, file_content):
    try:
        # Define the target path to save the file
        target_path = os.path.join("..", file_name)
        
        # Write the file content to the target location
        with open(target_path, "wb") as f:
            f.write(file_content.read())
        
        print(f"File saved successfully to: {target_path}")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")

def main():
    # URL of the file to download
    file_url = "https://storage.googleapis.com/mlcs-4f26e.appspot.com/user_files/wed_nesday/contract_1.pdf"

    # Download the file from Firebase
    file_name, file_content = download_file_from_url(file_url)

    if file_name and file_content:
        print(f"File downloaded: {file_name}")
        save_file(file_name, file_content)
    else:
        print("Failed to download the file. Please check the URL or your network connection.")

if __name__ == "__main__":
    main()

