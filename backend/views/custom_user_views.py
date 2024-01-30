# custom_user_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework import status
from ..serializers import UserSerializer, CustomUserSerializer, UserProfileUpdateSerializer
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
        # Check if the user has the permission to create a user
        # if not request.user.has_perm('auth.can_create_user'):
        #     return Response({'message': 'Permission denied. You do not have the required permission to create a user.'}, status=status.HTTP_403_FORBIDDEN)

        # Include additional information in the request data
        request.data['registered_by_id'] = request.user.UserID
        request.data['registered_by_fullname'] = request.user.FirstName

        # Handle file uploads to Firebase Storage
        cv_file = request.FILES.get('cv_file')
        contract_file = request.FILES.get('contract_file')

        cv_link = None
        contract_link = None

        if cv_file:
            folder = f"user_files/{request.data['FirstName']}"
            filename = "cv.pdf"

            # Ensure the content is properly read for InMemoryUploadedFile
            cv_content = cv_file.read()
            cv_file_Checksum = request.data.get('cv_file_checksum')

            if isinstance(cv_file, InMemoryUploadedFile):
                cv_link = upload_to_firebase_storage(folder, filename, cv_content, cv_file_Checksum)
            else:
                # Use the temporary file path
                local_file_path = cv_file.temporary_file_path()
                cv_link = upload_to_firebase_storage(folder, filename, local_file_path, cv_file_Checksum)

            print("CV Link Before Saving:", cv_link)

        if contract_file:
            folder = f"user_files/{request.data['FirstName']}"
            filename = "contract.pdf"

            # Ensure the content is properly read for InMemoryUploadedFile
            contract_content = contract_file.read()
            contract_file_Checksum = request.data.get('contract_file_checksum')
            if isinstance(contract_file, InMemoryUploadedFile):
                contract_link = upload_to_firebase_storage(folder, filename, contract_content, contract_file_Checksum)
            else:
                # Use the temporary file path
                local_file_path = contract_file.temporary_file_path()
                contract_link = upload_to_firebase_storage(folder, filename, local_file_path, contract_file_Checksum)

            print("Contract Link Before Saving:", contract_link)

        # Update the request data with the obtained links
        request.data['cv_link'] = cv_link
        request.data['contract_link'] = contract_link

        # Create a user serializer
        print("cv_link Before Serializer:", cv_link)
        print("contract_link Before Serializer:", contract_link)
        print("Request Data with Links:", request.data)
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data_view(request):
    """
    Dashboard data view providing statistics:
    1. Total Services, New Services in the current month
    2. Total Clients, New Clients in the current month
    3. A list of 10 recent services with client_name, date, and total cost

    Returns a JSON response containing the requested data.
    """
    # 1. Total Services, New Services in the current month
    total_services = Service.objects.count()
    start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_services_current_month = Service.objects.filter(start_time__gte=start_of_month).count()
    increase_rate_services = (total_services - new_services_current_month) / total_services
    increase_rate_services_percentage = increase_rate_services * 100
    


    # 2. Total Clients, New Clients in the current month
    total_clients = Client.objects.count()
    new_clients_current_month = Client.objects.filter(registrationDate__gte=start_of_month).count()
    increase_rate_clients = (total_clients - new_clients_current_month) / total_clients
    increase_rate_clients_percentage = increase_rate_clients * 100

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
    }

    return JsonResponse(response_data)
