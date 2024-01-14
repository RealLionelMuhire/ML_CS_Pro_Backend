from django.http import JsonResponse
from backend.google_sheets_auth import get_sheets_service  # Assuming your authentication code is in google_sheets_auth.py

def get_google_sheets_data(request):
    spreadsheet_id = '1c7DCtvZw0zdInkWw57H8Vz0_c0s7ioE9DjvoGKdg-yQ'
    sheet_title = 'Reservation'
    sheets_service = get_sheets_service()

    try:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get('sheets', [])

        for sheet in sheets:
            if sheet['properties']['title'] == sheet_title:
                sheet_id = sheet['properties']['sheetId']
                break

        if 'sheet_id' not in locals():
            raise Exception(f"Sheet with title '{sheet_title}' not found.")

        data = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_title}!A1:Z100"  # Adjust the range as needed
        ).execute()

        values = data.get('values', [])

        # Convert the data to JSON
        response_data = {
            'sheet_title': sheet_title,
            'values': values,
        }

        return JsonResponse(response_data)

    except Exception as e:
        error_message = f"Error retrieving data from Google Sheets: {e}"
        return JsonResponse({'error_message': error_message}, status=500)
