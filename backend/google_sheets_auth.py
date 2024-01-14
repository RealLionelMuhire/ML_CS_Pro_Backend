# backend/google_sheets_auth.py
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_sheets_service():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../credentials.json"))

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = path

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        service = build('sheets', 'v4', credentials=credentials)
        return service

    except Exception as e:
        print(f"Error initializing Google Sheets service: {e}")
        return None
