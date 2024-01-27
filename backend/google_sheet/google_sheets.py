# backend/google_sheet/google_sheets.py
from datetime import datetime
from django.utils.timezone import make_aware
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from ..models import Reservation, Options
from dateutil import parser

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "1c7DCtvZw0zdInkWw57H8Vz0_c0s7ioE9DjvoGKdg-yQ"

def fetch_reservation_data_from_sheets():
    SAMPLE_RANGE_NAME = "Reservations!A1:G1999"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds = None
    token_path = os.path.join(script_dir, "token.json")
    credentials_path = os.path.join(script_dir, "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
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

        # Get the latest formatted timestamp from the database or set a default value
        try:
            latest_timestamp = Reservation.objects.latest('timestamp').timestamp
            latest_timestamp = make_aware(datetime.strptime(latest_timestamp, "%Y-%m-%d %H:%M:%S"))
        except Reservation.DoesNotExist:
            latest_timestamp = make_aware(datetime.strptime("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"))

            # latest_timestamp = datetime.now()

        # print("===> Latest Formatted Timestamp ===>")
        # print(latest_timestamp)
        # print(type(latest_timestamp))
        
        # Parse date strings from the spreadsheet into datetime objects, skipping the header row
        values_with_datetime = [
            # (row[1], *row[2:])
            (make_aware(datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')), *row[2:])
            for row in values[1:]
        ]

        print("\n\n")
        print(values_with_datetime[0][5])
        print("===> Values with Datetime ===>")
        print(type(parser.parse(values_with_datetime[0][5])))
        print("\n\n")


        # Filter out rows with formatted timestamps equal to or earlier than the latest timestamp
        new_values = [row for row in values_with_datetime if row[0] > latest_timestamp]
        # print("===>This is new values===>")
        # print(new_values)

        return new_values

    except HttpError as err:
        print(f"An error occurred: {err}")
        return []

def fetch_options_data_from_sheets():
    SAMPLE_RANGE_NAME = "Options!A1:C1999"
    creds = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, "token.json")
    credentials_path = os.path.join(script_dir, "credentials.json")
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
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
        latest_timestamp = Options.objects.latest('available_datetime').available_datetime

        # Convert the latest timestamp to match the Excel format
        latest_timestamp_str = latest_timestamp.strftime("%m/%d/%Y %H:%M:%S")

        # Filter out rows with timestamps equal to or earlier than the latest timestamp
        new_values = [row for row in values if row[0] > latest_timestamp_str]

        # Update the Options model with new or changed data
        for row in new_values:
            existing_option = Options.objects.filter(available_datetime=row[0]).first()

            if existing_option:
                # Update existing row if availability status changes
                if existing_option.status != row[2]:
                    existing_option.status = row[2]
                    existing_option.save()
            else:
                # Create a new row if not existing
                Options.objects.create(
                    available_datetime=row[0],
                    day_of_week=row[1],
                    status=row[2]
                )

        return new_values

    except HttpError as err:
        print(f"An error occurred: {err}")
        return []
