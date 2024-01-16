from ..models import Reservation, Options
from django.http import HttpResponse
from ..google_sheet.google_sheets import fetch_options_data_from_sheets, fetch_reservation_data_from_sheets


def reservation_data_sheet(request):
    data_from_sheets =  fetch_reservation_data_from_sheets()

    # Save data to Reservation model
    for row in data_from_sheets:
        Reservation.objects.create(
            timestamp=row[0],
            email=row[1],
            full_name=row[2],
            phone_contact=row[3],
            service_title=row[4],
            appointment_datetime=row[5]
        )
    
    return HttpResponse("Data imported successfully.")

def options_data_sheet(request):
    data_from_sheets = fetch_options_data_from_sheets()

    # Save data to Options model
    for row in data_from_sheets:
        Options.objects.update_or_create(
            available_datetime=row[0],
            defaults={
                'day_of_week': row[1],
                'status': row[2],
            }
        )

    return HttpResponse("Options data imported successfully.")