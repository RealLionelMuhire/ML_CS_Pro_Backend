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
from ..helpers.firebase import upload_to_firebase_storage, delete_firebase_file, download_file_from_url
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..user_permissions import IsSuperuserOrManagerAdmin, IsSuperuserOrManagerAdminOrReadOnly, IsUser
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
import re
from urllib.parse import unquote, urlparse
import base64
import requests
from io import BytesIO
import os


class RegistrationView(APIView):
    """
    API view for user registration, requiring authentication and permission to create a user.
    Endpoint: POST /register/
    Request Payload: Requires 'auth.can_create_user' permission for access.
    Additional information (registered_by_id and registered_by_fullname) is added to the request data.
    """

    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin, IsSuperuserOrManagerAdminOrReadOnly]

    def post(self, request):
        """Handle POST requests for user registration."""
        # Make request.data mutable
        request.data._mutable = True
        
        # Include additional information in the request data
        request.data['registrarID'] = request.user.UserID
        request.data['registrarName'] = f"{request.user.FirstName} {request.user.LastName}"
        request.data['isActive'] = True
        
        # Handle file uploads to Firebase Storage
        cv_link, cv_msg = self.handle_file_upload(request, 'cv_file', 'cv.pdf')
        contract_link, contract_msg = self.handle_file_upload(request, 'contract_file', 'contract.pdf')
        national_id_link, national_id_msg = self.handle_file_upload(request, 'national_id_file', 'national_id.pdf')

        # Check if any file upload failed
        if any(link is None for link in [cv_link, contract_link, national_id_link]):
            # Delete uploaded files (if any) to avoid clutter in storage
            if cv_link:
                delete_firebase_file(cv_link)
            if contract_link:
                delete_firebase_file(contract_link)
            if national_id_link:
                delete_firebase_file(national_id_link)
            # Return failure message
            return Response({'message': 'File upload failed. Please try again.', 'errors': [cv_msg, contract_msg, national_id_msg]}, status=400)

        # Update the request data with the obtained links
        request.data.update({'cv_link': cv_link, 'contract_link': contract_link, 'national_id_link': national_id_link})

        # Make request.data immutable again
        request.data._mutable = False

        # Create a user serializer
        serializer = UserSerializer(data=request.data)

        try:
            if serializer.is_valid():
                # Save the user to the database
                user = serializer.save()
                return JsonResponse({'message': 'Registration successful', 'user_id': user.UserID})
            else:
                # Delete uploaded files (if any) to avoid clutter in storage
                if cv_link:
                    delete_firebase_file(cv_link)
                if contract_link:
                    delete_firebase_file(contract_link)
                if national_id_link:
                    delete_firebase_file(national_id_link)
                return JsonResponse({'message': 'Registration failed', 'errors': serializer.errors}, status=400)
        except Exception as e:
            # Delete uploaded files (if any) to avoid clutter in storage
            if cv_link:
                delete_firebase_file(cv_link)
            if contract_link:
                delete_firebase_file(contract_link)
            if national_id_link:
                delete_firebase_file(national_id_link)
            return JsonResponse({'message': 'Registration failed', 'error': str(e)}, status=500)

    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None

        if file:
            folder = f"user_files/{request.data['FirstName']}"
            file_content = file.read()

            if isinstance(file, InMemoryUploadedFile):
                file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link, msg = upload_to_firebase_storage(folder, file_name, local_file_path)

            return file_link, msg
        else:
            return None, f"No file found for {file_name} upload."


class HelloWorldView(APIView):
    """
    A simple API view to return a 'Hello, World!' message.
    Requires authentication for access.
    Endpoint: GET /hello-world/
    """

    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin]

    def get(self, request):
        """Handle GET requests and return a JSON response with a 'Hello, World!' message."""
        content = {'message': 'Hello, World!'}
        return Response(content)


class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)

        # Initialize files data dictionary
        files_data = {}

        # Download the CV file if the link exists
        if user.cv_link:
            print("Downloading CV")
            cv_file_name, cv_file_content = self.download_file_from_url(user.cv_link)
            if cv_file_content:
                files_data['cv_file'] = {
                    'file_name': cv_file_name,
                    'file_content': base64.b64encode(cv_file_content.getvalue()).decode('utf-8')
                }

        # Download the National ID file if the link exists
        if user.national_id_link:
            print("Downloading National ID")
            national_id_file_name, national_id_file_content = self.download_file_from_url(user.national_id_link)
            if national_id_file_content:
                files_data['national_id_file'] = {
                    'file_name': national_id_file_name,
                    'file_content': base64.b64encode(national_id_file_content.getvalue()).decode('utf-8')
                }

        # Combine user data and files data
        response_data = serializer.data
        response_data.update(files_data)

        return Response(response_data)

    def download_file_from_url(self, file_url):
        try:
            response = requests.get(file_url)
            if response.status_code == 200:
                file_name = unquote(os.path.basename(urlparse(file_url).path))
                file_content = BytesIO(response.content)
                print(f"downloading file.....")
                if file_name:
                    print(f"File name: {file_name} download complete")
                return file_name, file_content
            else:
                print(f"Download failed. Status code: {response.status_code}")
                return None, None
        except requests.RequestException as e:
            print(f"Error during download: {e}")
            return None, None
class UserDeactivateView(generics.UpdateAPIView, BaseUserAdmin):
    """
    API view for deactivating a user associated with the authenticated user.
    Requires authentication for access.
    Endpoint: PUT /user-deactivate/<int:pk>/
    """
    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin, IsSuperuserOrManagerAdminOrReadOnly]

    def patch(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)

        # Check if the authenticated user is the owner of the user
        # if request.user != user:
        #     return Response({'message': 'You do not have permission to deactivate this user.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user is already deactivated
        if not user.is_active:
            return Response({'message': 'User is already deactivated'}, status=status.HTTP_400_BAD_REQUEST)

        # Deactivate the user
        user.is_active = False
        user.is_staff = False
        user.deactivatorID = request.user.id
        user.deactivatorEmail = request.user.email
        user.deactivatorFirstName = request.user.first_name
        user.deactivationDate = timezone.now()
        user.save()

        # Update deactivator fields in CustomUser model
        request.user.deactivatorID = request.user.id
        request.user.deactivatorEmail = request.user.email
        request.user.deactivatorFirstName = request.user.first_name
        request.user.deactivationDate = timezone.now()
        request.user.save()

        return Response({'message': 'User deactivated successfully'}, status=status.HTTP_200_OK)



class UserActivateView(generics.UpdateAPIView):
    """
    API view for activating a user associated with the authenticated user.
    Requires authentication for access.
    Endpoint: PUT /user-activate/<int:pk>/
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserActivationSerializer
    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin, IsSuperuserOrManagerAdminOrReadOnly]
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
    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin]
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

    display_names_map = {
        'FirstName': 'First Name',
        'LastName': 'Last Name',
        'NationalID': 'National ID',
        'contact': 'Contact',
        'email': 'Email',
        'Address': 'Address',
        'contract_link': 'National ID LINK',
        'BirthDate': 'Date of Birth',
        'accessLevel': 'Access Level',
    }

    def get_object(self):
        return self.request.user  # Retrieve the profile of the authenticated user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Filter serializer data based on display_names_map
        user_data = {}
        for key, value in serializer.data.items():
            if key in self.display_names_map:
                user_data[self.display_names_map[key]] = value

        return Response(user_data)


class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Ensure that certain fields are not updated if they are empty
        exclude_empty_fields = ['FirstName', 'LastName', 'Address', 'NationalID', 'contact', 'email']

        # Exclude empty fields from request.data
        data_to_update = {key: value for key, value in request.data.items() if value or key not in exclude_empty_fields}

        # print("requests data are:", request.data)
        # print("request files:", request.FILES)

        # Check if there are files to be updated
        if 'national_id_file' in request.FILES:
            national_id_file = request.FILES['national_id_file']
            national_id_file_link, national_id_file_msg = self.handle_file_upload(request, 'national_id_file', 'national_id.pdf')
            if national_id_file_link:
                data_to_update['national_id_link'] = national_id_file_link
            else:
                return Response({'error': national_id_file_msg}, status=status.HTTP_400_BAD_REQUEST)

        if 'cv_file' in request.FILES:
            cv_file = request.FILES['cv_file']
            cv_file_link, cv_file_msg = self.handle_file_upload(request, 'cv_file', 'cv.pdf')
            if cv_file_link:
                data_to_update['cv_link'] = cv_file_link
            else:
                return Response({'error': cv_file_msg}, status=status.HTTP_400_BAD_REQUEST)
        

        # Validate and update other fields
        serializer = self.get_serializer(instance=self.get_object(), data=data_to_update, partial=True)
        serializer.is_valid(raise_exception=True)

        # Validate specific conditions for other fields
        if 'NationalID' in data_to_update and len(str(data_to_update['NationalID'])) < 5:
            return Response({'error': 'NationalID should be at least 5 digits.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'contact' in data_to_update and not self.is_valid_contact(data_to_update['contact']):
            return Response({'error': 'Invalid contact number.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'email' in data_to_update and not self.is_valid_email(data_to_update['email']):
            return Response({'error': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)

        # Perform the update
        self.perform_update(serializer)

        return Response(serializer.data)

    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None

        if file:
            folder = f"user_files{request.data['FirstName']}"
            file_content = file.read()

            if isinstance(file, InMemoryUploadedFile):
                file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link, msg = upload_to_firebase_storage(folder, file_name, local_file_path)
            # print(f"File link:  {file_link} and message is: {msg} ")

            return file_link, msg
        else:
            return None, f"No file found for {file_name} upload."


    def is_valid_contact(self, contact):
        # Your contact validation logic using regex
        phone_pattern = re.compile(r'^((\+[1-9]{1,4}[ -]?)|(\([0-9]{2,3}\)[ -]?)|([0-9]{2,4})[ -]?)*?[0-9]{3,4}[ -]?[0-9]{3,4}$')
        return bool(re.match(phone_pattern, contact))

    def is_valid_email(self, email):
        # Your email validation logic
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(re.match(email_pattern, email))


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
@permission_classes([IsAuthenticated, IsUser])
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