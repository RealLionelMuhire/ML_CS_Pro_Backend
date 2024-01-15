# backend/google_sheets.py
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from .models import Reservation

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "1c7DCtvZw0zdInkWw57H8Vz0_c0s7ioE9DjvoGKdg-yQ"
SAMPLE_RANGE_NAME = "Reservations!A1:F1999"

def fetch_data_from_sheets():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API to read existing data
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return []

        # Get the latest timestamp from the database
        latest_timestamp = Reservation.objects.latest('timestamp').timestamp

        new_values = [row for row in values if row[0] > latest_timestamp]

        return new_values

    except HttpError as err:
        print(f"An error occurred: {err}")
        return []
