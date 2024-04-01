from firebase_admin import credentials, initialize_app
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
import requests
from urllib.parse import urlparse, unquote
import os
from .firebase_initializer import initialize_firebase
import hashlib
from rest_framework.renderers import JSONRenderer
from io import BytesIO


def upload_to_firebase_storage(folder, file_name, file_content):
    initialize_firebase()
    service_account_key_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "serviceAccountKey.json"))

    try:
        # Specify your Firebase Storage bucket name
        bucket_name = "mlcs-de102.appspot.com"

        # Create a storage client with the explicit service account key
        # print("Creating storage client...")
        client = storage.Client.from_service_account_json(service_account_key_path)

        # Get the bucket
        # print(f"Getting bucket: {bucket_name}")
        bucket = client.bucket(bucket_name)

        # Specify the destination blob (file) in the storage
        destination_blob_name = f"{folder}/{file_name}"

        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(file_content)
        blob.make_public()

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

            # Debugging message
            print(f"Download successful. File name: {file_name}")

            # Create a BytesIO object to handle binary content
            file_content = BytesIO(response.content)

            # Return the file content and file name
            return file_name, file_content
        else:
            print(f"Download failed. Status code: {response.status_code}")
            return None, None

    except requests.RequestException as e:
        print(f"Error during download: {e}")
        return None, None