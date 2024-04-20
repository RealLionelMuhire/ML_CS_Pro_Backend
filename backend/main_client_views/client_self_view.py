import os
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from ..serializers import UserSerializer, ClientSerializer
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..firebase import upload_to_firebase_storage

class ClientSelfRegistrationView(APIView):
    """
    API view for user registration, requiring authentication and permission to create a user.
    Endpoint: POST /client/self-register-client/
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

        if request.data['citizenship'] == 'Other':
            request.data['citizenship'] = request.data['specifiedCitizenship']
        
        if 'NationalID' not in request.data:
            request.data['NationalID'] = request.data['passportIdNumber']
        
        # Handle file uploads to Firebase Storage
        cv_link = self.handle_file_upload(request, 'cv_file', 'cv.pdf')
        contract_link = self.handle_file_upload(request, 'contract_file', 'contract.pdf')
        national_id_link = self.handle_file_upload(request, 'national_id_file', 'national_id.pdf')
        passport_link = self.handle_file_upload(request, 'passport_file', 'passport.pdf')
        registration_certificate_link = self.handle_file_upload(request, 'registration_certificate', 'registration_certificate.pdf')

        # Update the request data with the obtained links
        request.data.update({'cv_link': cv_link, 'contract_link': contract_link, 'national_id_link': national_id_link, 'passport_link': passport_link, 'registration_certificate_link':registration_certificate_link})

        # Create a user serializer
        user_serializer = UserSerializer(data=request.data)

        try:
            if user_serializer.is_valid():
                try:
                    user = user_serializer.save()
                except Exception as e:
                    return Response({'message': 'User registration failed', 'errors': str(e)}, status=400)


                # Create a client serializer
                client_data = {
                    'user': user.UserID,
                    'firstName': user.FirstName,
                    'lastName': user.LastName,
                    'clientEmail': user.email,
                    'clientContact': user.contact,
                    'tinNumber': user.tinNumber,
                    'isActive': False,
                    'registrarID': user.UserID,
                    'registrarName': f'{user.FirstName} {user.LastName}',
                    # 'registration_certificate_link': user.registration_certificate_link,
                    'national_id_link': user.national_id_link,
                    'passport_link': user.passport_link,
                    'taxResidency': user.taxResidency,
                    'citizenship' : user.citizenship,
                    'passportIdNumber': user.passportIdNumber,
                    'preferredLanguage': user.preferredLanguage,
                    'registration_certificate_link': user.registration_certificate_link,
                    'countryOfResidence': user.countryOfResidence,
                    'NationalID': user.NationalID,
                    'birthDate': user.BirthDate,
                }
                client_serializer = ClientSerializer(data=client_data)

                if client_serializer.is_valid():
                    client_serializer.save()
                    return JsonResponse({'message': 'User and client registration successful', 'user_id': user.UserID})
                else:
                    # Client registration failed
                    if user:
                        try:
                            user.delete()
                        except Exception as e:
                            print(f"Error occurred while deleting user: {e}")
                    return Response({'message': 'Client registration failed', 'errors': client_serializer.errors}, status=400)
            else:
                # User registration failed
                return Response({'message': 'User registration failed', 'errors': user_serializer.errors}, status=400)
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
                print(f"File link: {file_link}")

        return file_link

