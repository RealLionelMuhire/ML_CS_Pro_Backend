# custom_user_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework import status
from ..serializers import UserSerializer, CustomUserSerializer, UserProfileUpdateSerializer, Reservation
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from ..models import CustomUser, Service, Client
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import generics
from django.http import JsonResponse
from decimal import Decimal
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from ..serializers import UserSerializer, UserActivationSerializer
from ..firebase import upload_to_firebase_storage, download_file_from_url
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO

class HelloWorldView(APIView):
    """
    A simple API view to return a 'Hello, World!' message.
    Requires authentication for access.
    Endpoint: GET /hello-world/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handle GET requests and return a JSON response with a 'Hello, World!' message."""
        content = {'message': 'Hello, World!'}
        return Response(content)


class RegistrationView(APIView):
    """
    API view for user registration, requiring authentication and permission to create a user.
    Endpoint: POST /register/
    Request Payload: Requires 'auth.can_create_user' permission for access.
    Additional information (registered_by_id and registered_by_fullname) is added to the request data.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handle POST requests for user registration."""
        # Include additional information in the request data
        request.data['registered_by_id'] = request.user.UserID
        request.data['registered_by_fullname'] = request.user.FirstName
        
        # Handle file uploads to Firebase Storage
        cv_link = self.handle_file_upload(request, 'cv_file', 'cv.pdf')
        contract_link = self.handle_file_upload(request, 'contract_file', 'contract.pdf')

        # Update the request data with the obtained links
        request.data.update({'cv_link': cv_link, 'contract_link': contract_link})

        # Create a user serializer
        serializer = UserSerializer(data=request.data)

        try:
            if serializer.is_valid():
                # Save the user to the database
                user = serializer.save()
                return JsonResponse({'message': 'Registration successful', 'user_id': user.UserID})
            else:
                print("Serializer errors:", serializer.errors)
                return Response({'message': 'Registration failed', 'errors': serializer.errors}, status=400)
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return Response({'message': 'Registration failed. Duplicate user.'}, status=status.HTTP_400_BAD_REQUEST)

    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None

        if file:
            folder = f"user_files/{request.data['FirstName']}"
            file_content = file.read()
            file_checksum = request.data.get(f'{file_key}_checksum')

            if isinstance(file, InMemoryUploadedFile):
                file_link = upload_to_firebase_storage(folder, file_name, file_content, file_checksum)
            else:
                local_file_path = file.temporary_file_path()
                file_link = upload_to_firebase_storage(folder, file_name, local_file_path, file_checksum)

            print(f"{file_name.capitalize()} Link Before Saving:", file_link)

        return file_link

class UserDeactivateView(generics.RetrieveUpdateAPIView, BaseUserAdmin):
    """
    API view for deactivating a user associated with the authenticated user.
    Requires authentication for access.
    Endpoint: PUT /user-deactivate/<int:pk>/
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['put']

    def update(self, request, *args, **kwargs):
        # print("===>Testing the update function==>")
        try:
            user = self.get_object()
            # Check if the authenticated user is the owner of the user
            if request.user != user:
                return Response({'message': 'You do not have permission to deactivate this user.'}, status=status.HTTP_403_FORBIDDEN)

            # Check if the user is already deactivated
            if not user.isActive:
                return Response({'message': 'User is already deactivated'}, status=status.HTTP_400_BAD_REQUEST)

            # Deactivate the user
            user.isActive = False
            user.is_staff = False
            user.deactivatorID = request.user.UserID
            user.deactivatorEmail = request.user.email
            user.deactivatorFirstName = request.user.FirstName
            user.deactivationDate = timezone.now()
            user.save()

            # Update activator fields in CustomUser model
            request.user.deactivatorID = request.user.UserID
            request.user.deactivatorEmail = request.user.email
            request.user.deactivatorFirstName = request.user.FirstName
            request.user.deactivationDate = timezone.now()
            request.user.save()

            return Response({'message': 'User deactivated successfully'})
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserActivateView(generics.UpdateAPIView):
    """
    API view for activating a user associated with the authenticated user.
    Requires authentication for access.
    Endpoint: PUT /user-activate/<int:pk>/
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserActivationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['put']


    # print("===>Testing the update function==>")
    # print("queryset is: ", queryset)

    def update(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            # Check if the authenticated user is the owner of the user
            if request.user != user:
                return Response({'message': 'You do not have permission to activate this user.'}, status=status.HTTP_403_FORBIDDEN)

            # Check if the user is already activated
            if user.isActive:
                return Response({'message': 'User is already activated'}, status=status.HTTP_400_BAD_REQUEST)

            # Activate the user
            user.isActive = True
            user.is_staff = True
            user.activatorID = request.user.UserID
            user.activatorEmail = request.user.email
            user.activatorFirstName = request.user.FirstName
            user.activationDate = timezone.now()
            user.save()

            # Update activator fields in the requesting user model
            request.user.activatorID = request.user.UserID
            request.user.activatorEmail = request.user.email
            request.user.activatorFirstName = request.user.FirstName
            request.user.activationDate = timezone.now()
            request.user.save()

            serializer = UserActivationSerializer(user)

            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserListView(APIView):
    """
    API view to retrieve a list of users.
    Endpoint: GET /api/users/
    """

    def get(self, request):
        """Handle GET requests for retrieving a list of users."""
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserProfileView(generics.RetrieveAPIView):
    """
    API view for retrieving the demographic data of the authenticated user.
    Requires authentication for access.
    Endpoint: GET /user-profile/
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the authenticated user
        return self.request.user

class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

def format_reserved_period(start_time, end_time):
    local_start_time = timezone.localtime(start_time)
    local_end_time = timezone.localtime(end_time)

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

    return reserved_period

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data_view(request):
    """
    Dashboard data view providing statistics:
    1. Total Services, New Services in the current month
    2. Total Clients, New Clients in the current month
    3. A list of 10 recent services with client_name, date, and total cost
    4. A list of 10 oldest reservations with name, email, phone contact, service to discuss, other services, start time, end time

    Returns a JSON response containing the requested data.
    """
    # 1. Total Services, New Services in the current month
    total_services = Service.objects.count()
    start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_services_current_month = Service.objects.filter(start_time__gte=start_of_month).count()
    increase_rate_services = 0 if total_services == 0 else round((total_services - new_services_current_month) / total_services, 2)
    increase_rate_services_percentage = round(increase_rate_services * 100, 1)

    # 2. Total Clients, New Clients in the current month
    total_clients = Client.objects.count()
    new_clients_current_month = Client.objects.filter(registrationDate__gte=start_of_month).count()
    increase_rate_clients = 0 if total_clients == 0 else round((total_clients - new_clients_current_month) / total_clients, 2)
    increase_rate_clients_percentage = round(increase_rate_clients * 100, 1)

    # 3. Total Reservations, New Reservations in the current month
    total_reservations = Reservation.objects.count()
    new_reservations_current_month = Reservation.objects.filter(startTime__gte=start_of_month).count()
    increase_rate_reservations = 0 if total_reservations == 0 else round((total_reservations - new_reservations_current_month) / total_reservations, 2)
    increase_rate_reservations_percentage = round(increase_rate_reservations * 100, 1)

    # 3. A list of 10 recent services with client_name, date, and total cost
    recent_services = Service.objects.order_by('-start_time')[:10]
    recent_services_data = [
        {
            'client_id': service.serviced_client_id,
            'client_name': service.client_name,
            'date': service.start_time.strftime('%Y-%m-%d'),
            'total_cost': '{}'.format(service.total_cost),
            'currency': '{}'.format(service.currency),
        }
        for service in recent_services
    ]

    # 4. A list of 10 oldest reservations with name, email, phone contact, service to discuss, other services, start time, end time
    oldest_reservations = Reservation.objects.filter(startTime__gte=timezone.now()).order_by('startTime')[:10]
    oldest_reservations_data = [
        {
            'name': reservation.fullName,
            'email': reservation.email,
            'phone_contact': reservation.clientContact,
            'service_to_discuss': reservation.servicesToDiscuss,
            'other_services': reservation.otherServices,
            'start_time': reservation.startTime.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': reservation.endTime.strftime('%Y-%m-%d %H:%M:%S'),
            'reserved_period': format_reserved_period(reservation.startTime, reservation.endTime),
        }
        for reservation in oldest_reservations
    ]

    # Prepare the response data
    response_data = {
        'total_services': total_services,
        'new_services_current_month': new_services_current_month,
        'increase_rate_services': increase_rate_services,
        'increase_rate_services_percentage': increase_rate_services_percentage,
        'total_clients': total_clients,
        'new_clients_current_month': new_clients_current_month,
        'increase_rate_clients': increase_rate_clients,
        'increase_rate_clients_percentage': increase_rate_clients_percentage,
        'recent_services': recent_services_data,
        'oldest_reservations': oldest_reservations_data,
        'total_reservations': total_reservations,
        'new_reservations_current_month': new_reservations_current_month,
        'increase_rate_reservations': increase_rate_reservations,
        'increase_rate_reservations_percentage': increase_rate_reservations_percentage,
    }

    return JsonResponse(response_data)