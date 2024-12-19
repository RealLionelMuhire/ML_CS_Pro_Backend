from google.cloud import storage
import requests
from urllib.parse import urlparse, unquote
import os
from .firebase_initializer import initialize_firebase
from io import BytesIO
from urllib.parse import urlparse
from decouple import config

def upload_to_firebase_storage(folder, file_name, file_content):
    initialize_firebase()
    print("after firebase initialize, in upload_to_firebase_storage fx..")

    service_account_key = {
        "type": config("FIREBASE_TYPE"),
        "project_id": config("FIREBASE_PROJECT_ID"),
        "private_key_id": config("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": config("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": config("FIREBASE_CLIENT_EMAIL"),
        "client_id": config("FIREBASE_CLIENT_ID"),
        "auth_uri": config("FIREBASE_AUTH_URI"),
        "token_uri": config("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": config("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": config("FIREBASE_CLIENT_X509_CERT_URL"),
    }
    try:
        print(f"Uploading file: {file_name}")
        print(f"File content size: {len(file_content)} bytes")


        # Specify your Firebase Storage bucket name
        bucket_name = "mlcs-4f26e.appspot.com"

        # Create a storage client with the explicit service account key
        client = storage.Client.from_service_account_info(service_account_key)

        # Get the bucket
        bucket = client.bucket(bucket_name)

        # Specify the destination blob (file) in the storage
        destination_blob_name = f"{folder}/{file_name}"

        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(file_content)
        blob.make_public()

        public_url = blob.public_url
        # print("\n\n In upload firebase,File uploaded successfully to Firebase Storage. filename is :", file_name)
        # print("\n\nPublic URL:", public_url)
        return (public_url, f"File uploaded successfully to {public_url}")

    except FileNotFoundError as e:
        # print(f"\nupload_firebase: =====> An: Error: {e.filename} not found.")
        return (None, f"Error: {e.filename} not found.")
    except Exception as e:
        # print(f"\n in upload_firebase: =====> An unexpected error occurred: {e}")
        return (None, f"An unexpected error occurred: {e}")

def delete_firebase_file(public_url):
    initialize_firebase()
    firebase_credentials = {
        "type": config("FIREBASE_TYPE"),
        "project_id": config("FIREBASE_PROJECT_ID"),
        "private_key_id": config("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": config("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": config("FIREBASE_CLIENT_EMAIL"),
        "client_id": config("FIREBASE_CLIENT_ID"),
        "auth_uri": config("FIREBASE_AUTH_URI"),
        "token_uri": config("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": config("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": config("FIREBASE_CLIENT_X509_CERT_URL"),
    }
    service_account_key = firebase_credentials

    try:
        # Create a storage client with the explicit service account key
        client = storage.Client.from_service_account_info(service_account_key)

        # Parse the public URL to get the bucket name and blob name
        parsed_url = urlparse(public_url)
        bucket_name = parsed_url.netloc
        blob_name = parsed_url.path.lstrip('/')

        # Get the bucket
        bucket = client.bucket(bucket_name)

        # Specify the blob to be deleted
        blob = bucket.blob(blob_name)

        # Delete the blob
        blob.delete()

        return (public_url, f"File {blob_name} deleted successfully.")
    
    except Exception as e:
        return (None, f"An unexpected error occurred: {e}")

def download_file_from_url(file_url):
    try:
        response = requests.get(file_url)
       
        if response.status_code == 200:
            file_name = unquote(os.path.basename(urlparse(file_url).path))
            file_content = BytesIO(response.content)
            return file_name, file_content
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
            return None, None
    except requests.RequestException as e:
        print(f"RequestException: {e}")
        return None, None
