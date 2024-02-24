# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from ..models import Reservation
from ..serializers import ReservationSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

class RegisterReservationView(APIView):
    """
    API view for registering a reservation.

    Requires no authentication for access.

    Endpoint: POST /api/register-reservation/
    """

    permission_classes = [AllowAny]

    def post(self, request, format=None):
        # registering a new reservation

        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Reservation registered successfully'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListReservedPeriodsView(APIView):
    """
    API view for listing reserved periods with startTime and endTime.

    Requires no authentication for access.

    Endpoint: GET /api/list-reserved-periods/
    """

    permission_classes = [AllowAny]

    def get(self, request, format=None):
        """
        Get a list of reserved periods with startTime and endTime.

        Returns:
        - Success: Returns a list of reserved periods
        - Failure: Returns an error message
        """

        reservations = Reservation.objects.all()
        serializer = ReservationSerializer(reservations, many=True)

        # Extract only the required fields
        extracted_data = [{'startTime': item['startTime'], 'endTime': item['endTime']} for item in serializer.data]

        return Response({'reserved_periods': extracted_data})


class ListReservationsStartingTodayView(APIView):
    """
    API view for listing all reservations starting from today.

    Requires no authentication for access.

    Endpoint: GET /api/list-reservations-starting-today/
    """

    permission_classes = [AllowAny]

    def get(self, request, format=None):
        """
        Get a list of all reservations starting from today.

        Returns:
        - Success: Returns a list of reservations
        - Failure: Returns an error message
        """

        # Filter reservations starting from today
        current_date = timezone.now().date()
        reservations = Reservation.objects.filter(startTime__gte=current_date).order_by('startTime')

        # Add 'reserved_period' to each reservation and append it to serialized data
        serialized_data = []
        for reservation in reservations:
            reserved_period = f"{timezone.localtime(reservation.startTime).strftime('%a %d, %b %Y at %I %p')} - {timezone.localtime(reservation.endTime).strftime('%I %p')}"
            serialized_item = ReservationSerializer(reservation).data
            serialized_item['reserved_period'] = reserved_period
            serialized_data.append(serialized_item)

        return Response(serialized_data)

class ListPastReservationsView(APIView):
    """
    API view for listing all past reservations starting from today.

    Requires no authentication for access.

    Endpoint: GET /api/list-past-reservations/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        Get a list of all past reservations starting from today.

        Returns:
        - Success: Returns a list of past reservations
        - Failure: Returns an error message
        """

        # Filter past reservations starting from today (excluding today)
        current_date = timezone.now().date()
        past_reservations = Reservation.objects.filter(startTime__lt=current_date).order_by('startTime')

        serialized_data = []
        for reservation in past_reservations:
            reserved_period = f"{timezone.localtime(reservation.startTime).strftime('%a %d, %b %Y at %I %p')} - {timezone.localtime(reservation.endTime).strftime('%I %p')}"
            serialized_item = ReservationSerializer(reservation).data
            serialized_item['reserved_period'] = reserved_period
            serialized_data.append(serialized_item)

        return Response(serialized_data)