# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from ..models import Reservation
from ..serializers import ReservationSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

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
            local_start_time = timezone.localtime(reservation.startTime)
            local_end_time = timezone.localtime(reservation.endTime)

            if local_start_time.date() != local_end_time.date():
                # Different days, format accordingly
                reserved_period = (
                    f"{local_start_time.strftime('%a %d, %b %Y at %I %p')} - "
                    f"{local_end_time.strftime('%a %d, %b %Y at %I %p')}"
                )
            else:
                # Same day
                reserved_period = (
                    f"{local_start_time.strftime('%a %d, %b %Y at %I %p')} - "
                    f"{local_end_time.strftime('%I %p')}"
                )

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
            local_start_time = timezone.localtime(reservation.startTime)
            local_end_time = timezone.localtime(reservation.endTime)

            if local_start_time.date() != local_end_time.date():
                # Different days, format accordingly
                reserved_period = (
                    f"{local_start_time.strftime('%a %d, %b %Y at %I %p')} - "
                    f"{local_end_time.strftime('%a %d, %b %Y at %I %p')}"
                )
            else:
                # Same day
                reserved_period = (
                    f"{local_start_time.strftime('%a %d, %b %Y at %I %p')} - "
                    f"{local_end_time.strftime('%I %p')}"
                )

            serialized_item = ReservationSerializer(reservation).data
            serialized_item['reserved_period'] = reserved_period
            serialized_data.append(serialized_item)

        return Response(serialized_data)


class ListAllReservationsView(APIView):
    """
    API view for listing all reservations.

    Requires no authentication for access.

    Endpoint: GET /api/list-all-reservations/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        Get a list of all reservations.

        Returns:
        - Success: Returns a list of all reservations
        - Failure: Returns an error message
        """

        reservations = Reservation.objects.all().order_by('startTime')

        serialized_data = []
        for reservation in reservations:
            local_start_time = timezone.localtime(reservation.startTime)
            local_end_time = timezone.localtime(reservation.endTime)

            if local_start_time.date() != local_end_time.date():
                # Different days, format accordingly
                reserved_period = (
                    f"{local_start_time.strftime('%a %d, %b %Y at %I %p')} - "
                    f"{local_end_time.strftime('%a %d, %b %Y at %I %p')}"
                )
            else:
                # Same day
                reserved_period = (
                    f"{local_start_time.strftime('%a %d, %b %Y at %I %p')} - "
                    f"{local_end_time.strftime('%I %p')}"
                )

            serialized_item = ReservationSerializer(reservation).data
            serialized_item['reserved_period'] = reserved_period
            serialized_data.append(serialized_item)

        return Response(serialized_data)

class UserRegisterReservationView(APIView):
    """
    API view for registering a reservation by an authenticated user.

    Requires authentication for access.

    Endpoint: POST /api/user-register-reservation/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Get authenticated user details
        user = request.user

        # Check if the user is authenticated
        if not user.is_authenticated:
            return Response({'error': 'Authentication required to register a reservation.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve data from the request
        start_time = request.data.get('startTime')
        end_time = request.data.get('endTime')
        services_to_discuss = request.data.get('servicesToDiscuss')

        # Check for overlapping reservations
        overlapping_reservations = Reservation.objects.filter(
            startTime__lt=end_time,
            endTime__gt=start_time
        )

        if overlapping_reservations.exists():
            return Response({'error': 'The selected period is already booked.'}, status=status.HTTP_400_BAD_REQUEST)

        # Set reservation details based on user information
        reservation_data = {
            'fullName': f"{user.FirstName} {user.LastName}",
            'email': user.email,
            'clientContact': user.contact,
            'startTime': start_time,
            'endTime': end_time,
            'servicesToDiscuss': services_to_discuss,
        }

        # Create and save the reservation
        reservation_serializer = ReservationSerializer(data=reservation_data)
        if reservation_serializer.is_valid():
            reservation_serializer.save()
            return Response({'message': 'Reservation registered successfully'})
        else:
            return Response(reservation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting an reservation.
    Requires authentication for access.
    Endpoint: GET /api/reservations/<int:pk>/ (Retrieve an reservation)
              PUT /api/reservations/<int:pk>/ (Update an reservation)
              DELETE /api/reservations/<int:pk>/ (Delete an reservation)
    """

    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve an reservation.
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update an reservation.
        """
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an reservation.
        """
        return super().destroy(request, *args, **kwargs)
