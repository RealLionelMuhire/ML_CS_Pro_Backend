import os
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from ..serializers import UserSerializer
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from django.db.models import F
from ..models import Transaction
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..firebase import upload_to_firebase_storage
from ..views.client_views import ClientRegistrationView
from rest_framework.request import Request

class ClientSelfRegistrationView(APIView):
    """
    API view for user registration, requiring authentication and permission to create a user.
    Endpoint: POST /register/
    Request Payload: Requires 'auth.can_create_user' permission for access.
    Additional information (registered_by_id and registered_by_fullname) is added to the request data.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle POST requests for user registration."""
        # Include additional information in the request data
        request.data['registrarID'] = 0
        request.data['registrarName'] = f"Self Registered"
        request.data['isActive'] = False
        request.data['is_staff'] = False
        request.data['accessLevel'] = 'Client'
        
        # Handle file uploads to Firebase Storage
        cv_link = self.handle_file_upload(request, 'cv_file', 'cv.pdf')
        contract_link = self.handle_file_upload(request, 'contract_file', 'contract.pdf')
        national_id_link = self.handle_file_upload(request, 'national_id_file', 'national_id.pdf')
        passport_link = self.handle_file_upload(request, 'passport_file', 'passport.pdf')

        # Update the request data with the obtained links
        request.data.update({'cv_link': cv_link, 'contract_link': contract_link, 'national_id_link': national_id_link, 'passport_link': passport_link})

        # Create a user serializer
        serializer = UserSerializer(data=request.data)

        try:
            if serializer.is_valid():
                user = serializer.save()
                # Prepare request data for client registration
                client_request_data = {
                    'user': user.UserID,
                    'firstName': user.FirstName,
                    'lastName': user.LastName,
                    'clientEmail': user.email,
                    'clientContact': user.contact,
                    'tinNumber': user.tinNumber,
                    'isActive': False,
                    'registrarID': user.UserID,
                    'registrarName': f'{user.FirstName} {user.LastName}',
                    'registrationCertificate_link': user.registrationCertificate_link,
                    'national_id_link': user.national_id_link,
                    'passport_link': user.passport_link,
                    # Add more data if needed
                }

                # Execute ClientRegistrationView
                client_registration_view = ClientRegistrationView.as_view()

                request._request.data = client_request_data

                response = client_registration_view(request._request)
                
                if response.status_code == status.HTTP_201_CREATED:
                    # Registration was successful
                    return JsonResponse({'message': 'User and client registration successful', 'user_id': user.UserID, 'client_id': response.data.get('client_id', None)})
                else:
                    # Registration failed
                    return JsonResponse({'message': 'User registration successful but client registration failed'}, status=400)
            else:
                # User registration failed
                return Response({'message': 'Registration failed', 'errors': serializer.errors}, status=400)
        except IntegrityError as e:
            # IntegrityError occurred
            return Response({'message': 'Registration failed. Duplicate registration.'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None

        if file:
            folder = f"user_files/{request.data['FirstName']}"
            file_content = file.read()

            if isinstance(file, InMemoryUploadedFile):
                file_link = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link = upload_to_firebase_storage(folder, file_name, local_file_path)

        return file_link
