# backend/google_sheets_auth.py
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

path = os.path.join("../../", "client_secret.json")

def get_authenticated_service(path, api_name, api_version):
    credentials = service_account.Credentials.from_service_account_file(path, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    service = build(api_name, api_version, credentials=credentials)
    return service
