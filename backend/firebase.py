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

def calculate_checksum(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()

def upload_to_firebase_storage(folder, file_name, file_content, expected_checksum):
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

        # Calculate checksum of the file content
        calculated_checksum = calculate_checksum(file_content)
        # print(f"Calculated checksum: {calculated_checksum}")
        # print(f"Expected checksum: {expected_checksum}")

        # Compare the computed checksum with the expected_checksum
        if calculated_checksum == expected_checksum:
            # Upload the file content to Cloud Storage
            # print(f"Uploading file to {destination_blob_name}...")
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_string(file_content)  # Use upload_from_string for content in bytes
            blob.make_public()

            # Get public URL
            public_url = blob.public_url
            print(f"File uploaded successfully. Public URL: {public_url}")
            return public_url
        else:
            print("Error: Checksum verification failed. Aborting upload.")

    except FileNotFoundError as e:
        print(f"Error: {e.filename} not found.")
    except GoogleCloudError as e:
        print(f"Google Cloud Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None


# class BinaryJSONRenderer(JSONRenderer):
#     media_type = 'application/json'

#     def render(self, data, accepted_media_type=None, renderer_context=None):
#         for key, value in data.items():
#             if isinstance(value, bytes):
#                 data[key] = value.decode('utf-8', errors='replace')
#         return super().render(data, accepted_media_type, renderer_context)

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