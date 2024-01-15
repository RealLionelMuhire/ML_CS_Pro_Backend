from ..models import Reservation
from ..google_sheets import fetch_reservation_data_from_sheets
from django.http import HttpResponse

def reservation_data_sheet(requests):
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