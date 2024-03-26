# views/client_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import ClientSerializer
from ..models import Client
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from django.db import IntegrityError
from rest_framework import status
from django.utils import timezone
from ..firebase import upload_to_firebase_storage, download_file_from_url
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..user_permissions import IsSuperuserOrManagerAdmin

class ClientRegistrationView(APIView):
    """
    API view for registering a client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: POST /client-registration/
    """

    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin]

    def post(self, request):
        """Handle POST requests for client registration."""
        # Retrieve the user from the authenticated request
        user = request.user

        # Combine the user data with the client data
        request_data = request.data
        request_data['user'] = user.UserID

        # Handle file uploads to Firebase Storage
        signature_link = self.handle_file_upload(request, 'signature_file', 'signature.pdf')
        bankStatement_link = self.handle_file_upload(request, 'bankStatement_file', 'bankStatement.pdf')
        professionalReference_link = self.handle_file_upload(request, 'professionalReference_file', 'professionalReference.pdf')

        # Update the request data with the obtained links
        request.data.update({'signature_link': signature_link, 'bankStatement_link': bankStatement_link, 'professionalReference_link': professionalReference_link})

        try:
            # Set the registrar information
            request_data['registrarID'] = user.UserID
            request_data['registrarEmail'] = user.email
            request_data['registrarFirstName'] = user.FirstName

            # Create the serializer
            serializer = ClientSerializer(data=request_data)

            if serializer.is_valid():
                # Save the client with the associated user and registrar
                client = serializer.save()

                return Response({'message': 'Client registration successful', 'client_id': client.id})
            else:
                return Response({'message': 'Client registration failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return Response({'message': 'Client registration failed. Duplicate client.'}, status=status.HTTP_400_BAD_REQUEST)
    
    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None

        if file:
            folder = f"client_files/{request.data['firstName']}_{request.data['lastName']}"
            file_content = file.read()
            file_checksum = request.data.get(f'{file_key}_checksum')

            if isinstance(file, InMemoryUploadedFile):
                file_link = upload_to_firebase_storage(folder, file_name, file_content, file_checksum)
            else:
                local_file_path = file.temporary_file_path()
                file_link = upload_to_firebase_storage(folder, file_name, local_file_path, file_checksum)

            print(f"{file_name.capitalize()} Link Before Saving:", file_link)

        return file_link

class ClientDeactivateView(generics.RetrieveUpdateAPIView):
    """
    API view for deactivating a client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: PUT /client-deactivate/<int:pk>/
    """

    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """Handle PUT requests to deactivate a client."""
        try:
            client = self.get_object()
            # Check if the authenticated user is the owner of the client
            # if request.user != client.user:
            #     return Response({'message': 'You do not have permission to deactivate this client.'}, status=status.HTTP_403_FORBIDDEN)

            # Check if the client is already deactivated
            if not client.isActive:
                return Response({'message': 'Client is already deactivated'}, status=status.HTTP_400_BAD_REQUEST)

            # Deactivate the client
            client.isActive = False
            client.deactivatorID = request.user.UserID
            client.deactivatorEmail = request.user.email
            client.deactivatorFirstName = request.user.FirstName
            client.deactivationDate = timezone.now()
            client.save()

            return Response({'message': 'Client deactivated successfully'})
        except Client.DoesNotExist:
            return Response({'message': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

class ClientActivateView(generics.RetrieveUpdateAPIView):
    """
    API view for activating a client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: PUT /client-activate/<int:pk>/
    """

    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """Handle PUT requests to activate a client."""
        try:
            client = self.get_object()
            # Check if the authenticated user is the owner of the client
            # if request.user != client.user:
            #     return Response({'message': 'You do not have permission to activate this client.'}, status=status.HTTP_403_FORBIDDEN)

            # Check if the client is already activated
            if client.isActive:
                return Response({'message': 'Client is already activated'}, status=status.HTTP_400_BAD_REQUEST)

            # Activate the client
            client.isActive = True
            client.activatorID = request.user.UserID
            client.activatorEmail = request.user.email
            client.activatorFirstName = request.user.FirstName
            client.activationDate = timezone.now()
            client.save()

            return Response({'message': 'Client activated successfully'})
        except Client.DoesNotExist:
            return Response({'message': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_clients(request):
    """
    API view for searching clients based on a query parameter.
    Requires authentication for access.
    Endpoint: GET /search-clients/?q=<search_query>
    """

    # Get query parameters from the request
    search_query = request.query_params.get('q', '')

    # Perform the search
    clients = Client.objects.filter(full_name__icontains=search_query)

    # Serialize the results
    serializer = ClientSerializer(clients, many=True)

    return Response(serializer.data)


class AddFieldToClientView(APIView):
    """
    API view for adding a new field to a client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: POST /add-field-to-client/<int:client_id>/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, client_id):
        """Handle POST requests to add a new field to a client."""
        # Get the client instance
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({'message': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to modify this client
        if request.user != client.user:
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # Get the field value from the request data
        field_value = request.data.get('new_field', None)

        # Add the new field to the client
        if field_value is not None:
            client.new_field = field_value
            client.save()
            return Response({'message': 'Field added successfully'})
        else:
            return Response({'message': 'Invalid field value'}, status=status.HTTP_400_BAD_REQUEST)

        return file_link

class ListClientsView(APIView):
    """
    API view for listing all clients associated with the authenticated user.
    Requires authentication for access.
    Endpoint: GET /list-clients/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handle GET requests to list all clients."""
        clients = Client.objects.all()

        # Serialize the results
        serializer = ClientSerializer(clients, many=True)

        return Response(serializer.data)

class ClientListByIdView(generics.ListAPIView):
    """
    API view for retrieving a list of clients by IDs.
    Requires authentication for access.
    Endpoint: GET /clients-list-by-id/?ids=1,2,3
    """

    permission_classes = [IsAuthenticated]

    display_names_map = {
    'firstName': 'First Name',
    'lastName': 'Last Name',
    'taxResidency': 'Tax Residency',
    'tinNumber': 'TIN Number',
    'citizenship': 'Citizenship',
    'birthDate': 'Birth Date',
    'countryOfResidence': 'Country of Residence',
    'passportIdNumber': 'Passport ID Number',
    'countryOfIssue': 'Country of Issue',
    'passportExpiryDate': 'Passport Expiry Date',
    'NameOfEntity': 'Name of Entity',
    'PrevNameOfEntity': 'Previous Name of Entity',
    'TypeOfEntity': 'Type of Entity',
    'TypeOfLicense': 'Type of License',
    'sharePercent': 'Share Percent',
    'currentAddress': 'Current Address',
    'clientContact': 'Client Contact',
    'clientEmail': 'Client Email',
    'preferredLanguage': 'Preferred Language',
    'registrarID': 'Registrar ID',
    'registrarEmail': 'Registrar Email',
    'registrarFirstName': 'Registrar First Name',
    'registrationDate': 'Registration Date',
    'isActive': 'Is Active',
    'activatorID': 'Activator ID',
    'activatorEmail': 'Activator Email',
    'activatorFirstName': 'Activator First Name',
    'activationDate': 'Activation Date',
    'deactivatorID': 'Deactivator ID',
    'deactivatorEmail': 'Deactivator Email',
    'deactivatorFirstName': 'Deactivator First Name',
    'deactivationDate': 'Deactivation Date',
    'designation': 'Designation',
    'introducerName': 'Introducer Name',
    'introducerEmail': 'Introducer Email',
    'contactPersonName': 'Contact Person Name',
    'contactPersonEmail': 'Contact Person Email',
    'contactPersonPhone': 'Contact Person Phone',
    'authorisedName': 'Authorised Name',
    'authorisedEmail': 'Authorised Email',
    'authorisedPersonContact': 'Authorised Person Contact',
    'authorisedCurrentAddress': 'Authorised Current Address',
    'authorisedRelationship': 'Authorised Relationship',
    'isPep': 'Is PEP',
    'signature_link': 'Signature',
    'bankStatement_link': 'Bank Statement',
    'professionalReference_link': 'Professional Reference',
    'incorporationDate': 'Incorporation Date',
    'countryOfIncorporation': 'Country of Incorporation',
    'registeredOfficeAddress': 'Registered Office Address',
    'businessActivity': 'Business Activity',
    'countryOfOperation': 'Country of Operation',
    }

    def get_queryset(self):
        # Get the list of client IDs from the query parameters
        client_ids_str = self.request.query_params.get('ids', '')
        client_ids = [int(client_id) for client_id in client_ids_str.split(',') if client_id.isdigit()]

        # Filter and retrieve clients based on the provided IDs
        queryset = Client.objects.filter(id__in=client_ids)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serialized_clients = []

        for client_id in [int(client_id) for client_id in self.request.query_params.get('ids', '').split(',')]:
            client = get_object_or_404(queryset, id=client_id)
            serializer = ClientSerializer(client)
            serialized_data = serializer.data

            # Rename the keys based on display names map
            renamed_data = {self.display_names_map.get(key, key): value for key, value in serialized_data.items() if key in self.display_names_map}

            serialized_clients.append(renamed_data)

        return Response(serialized_clients)

