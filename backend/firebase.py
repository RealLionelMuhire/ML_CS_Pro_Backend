from firebase_admin import credentials, initialize_app
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
import requests
from urllib.parse import urlparse, unquote
import os


def upload_to_firebase_storage(service_account_key_path, folder, file_name, local_file_path):
    try:
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(service_account_key_path)
        initialize_app(cred)

        # Specify your Firebase Storage bucket name
        bucket_name = "mlcs-de102.appspot.com"

        # Create a storage client with the explicit service account key
        client = storage.Client.from_service_account_json(service_account_key_path)

        # Get the bucket
        bucket = client.bucket(bucket_name)

        # Specify the destination blob (file) in the storage
        destination_blob_name = f"{folder}/{file_name}"

        # Upload the local file to Cloud Storage
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)
        blob.make_public()

        # Get public URL
        public_url = blob.public_url
        return public_url

    except FileNotFoundError as e:
        print(f"Error: {e.filename} not found.")
    except GoogleCloudError as e:
        print(f"Google Cloud Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None

def download_file_from_url(file_url):
    try:
        # Make a GET request to the file URL
        response = requests.get(file_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract the file name from the URL
            file_name = unquote(os.path.basename(urlparse(file_url).path))

            # Return the file content and file name
            return file_name, response.content
        else:
            print(f"Download failed. Status code: {response.status_code}")
            return None, None

    except requests.RequestException as e:
        print(f"Error during download: {e}")
        return None, None