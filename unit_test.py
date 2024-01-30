#!/usr/bin/env python3
import unittest
import tempfile
import os
from unittest.mock import patch
from backend.firebase import upload_to_firebase_storage, download_file_from_url

class FirebaseStorageTest(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory and file for testing
        self.test_folder = "test_folder"
        self.test_file_name = "test_file.txt"
        self.test_local_file_path = os.path.join(tempfile.gettempdir(), self.test_file_name)

        with open(self.test_local_file_path, "w") as test_file:
            test_file.write("Test content")

    def tearDown(self):
        # Clean up the temporary directory and file
        os.remove(self.test_local_file_path)

    @patch("backend.firebase.initialize_app")
    @patch("backend.firebase.storage.Client.from_service_account_json")
    def test_upload_to_firebase_storage(self, mock_client, mock_init_app):
        # Mock Firebase storage client and initialize_app
        mock_blob = mock_client().bucket().blob()
        mock_blob.public_url = "https://storage.googleapis.com/mlcs-de102.appspot.com/test_folder/test_file.txt"

        # Call the function
        print("Calling upload_to_firebase_storage")
        public_url = upload_to_firebase_storage(self.test_folder, self.test_file_name, self.test_local_file_path)
        print(f"Public URL: {public_url}")

        # Assert the public URL
        self.assertEqual(public_url, mock_blob.public_url)

    @patch("backend.firebase.requests.get")
    def test_download_file_from_url(self, mock_requests_get):
        # Mock the response from requests.get
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.content = b"Test content"
        mock_requests_get.return_value = mock_response

        # Call the function
        print("Calling download_file_from_url")
        file_name, file_content = download_file_from_url("https://example.com/test_file.txt")
        print(f"File Name: {file_name}, File Content: {file_content}")

        # Assert the file name and content
        self.assertEqual(file_name, "test_file.txt")
        self.assertEqual(file_content, b"Test content")

    @patch("backend.firebase.requests.get")
    def test_download_file_from_url_failure(self, mock_requests_get):
        # Mock the response from requests.get with a failure status code
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        # Call the function
        print("Calling download_file_from_url_failure")
        file_name, file_content = download_file_from_url("https://example.com/nonexistent_file.txt")
        print(f"File Name: {file_name}, File Content: {file_content}")

        # Assert that the function returns None for file_name and file_content
        self.assertIsNone(file_name)
        self.assertIsNone(file_content)

if __name__ == "__main__":
    unittest.main()
