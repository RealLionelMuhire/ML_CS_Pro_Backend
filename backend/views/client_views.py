# views/client_views.py

from django.forms import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import ClientSerializer, UncompletedClientSerializer, UpdateUncompletedClientSerializer
from ..models import Client, UncompletedClient, CustomUser
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from django.db import IntegrityError, transaction
from rest_framework import status
from django.utils import timezone
from ..helpers.firebase import upload_to_firebase_storage, delete_firebase_file
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..user_permissions import IsSuperuserOrManagerAdmin
from django.http import JsonResponse
import base64
import os
from urllib.parse import unquote, urlparse
from io import BytesIO
import requests
import logging
import json


class ClientRegistrationView(APIView):
    """
    API view for registering a client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: POST /client-registration/
    """

    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin]

    def post(self, request):
        """Handle POST requests for client registration."""
        user = request.user

        # Make request.data mutable
        request.data._mutable = True

        # Combine the user data with the client data
        request.data['user'] = user.UserID

        # Handle file uploads to Firebase Storage
        file_keys = [
            'signature_file', 'bankStatement_file', 'professionalReference_file', 
            'confirmationLetter_file', 'custody_accounts_file', 'source_of_funds_file', 
            'payslips_file', 'due_diligence_file', 'financial_statements_file', 
            'proof_of_ownership_file', 'lease_agreement_file', 'documentary_evidence_file', 
            'bank_statement_proceeds_file', 'bank_statement_file', 'cdd_documents_file', 
            'bank_statements_file', 'bank_statements_proceeds_file', 'notarised_documents_file', 
            'letter_from_donor_file', 'donor_source_of_wealth_file', 'donor_bank_statement_file', 
            'letter_from_relevant_org_file', 'lottery_bank_statement_file', 'creditor_agreement_file', 
            'creditor_cdd_file', 'creditor_bank_statement_file', 'legal_document_file', 
            'notary_letter_file', 'executor_letter_file', 'loan_agreement_file', 
            'loan_bank_statement_file', 'related_third_party_loan_agreement_file', 
            'related_third_party_cdd_file', 'related_third_party_bank_statement_file', 
            'unrelated_third_party_loan_agreement_file', 'unrelated_third_party_cdd_file', 
            'unrelated_third_party_bank_statement_file', 'signed_letter_from_notary_file', 
            'property_contract_file', 'insurance_pay_out_file', 'retirement_annuity_fund_statement_file', 
            'passport_file', 'utility_file', 'wealth_file', 'cv_file', 'funds_file', 
            'source_of_wealth_file', 'principals_identification_file', 'shareholders_file', 
            'declaration_of_trust_file', 'certificate_of_registration_file', 'deed_of_retirement_file', 
            'business_plan_file', 'registered_office_file', 'register_of_trustee_file', 
            'proof_of_source_of_funds_file', 'proof_of_source_of_wealth_file', 
            'latest_accounts_or_bank_statements_file', 'licence_file', 'certificate_of_incumbency_file', 
            'charter_file', 'latest_accounts_file', 'identification_documents_of_the_principals_of_the_foundation_file'
        ]
        
        for file_key in file_keys:
            file_name = file_key.replace('_file', '') + '.pdf'
            file_link, msg = self.handle_file_upload(request, file_key, file_name)
            request.data[file_key.replace('_file', '_link')] = file_link

        try:
            # Set the registrar information
            request.data['registrarID'] = user.UserID
            request.data['registrarEmail'] = user.email
            request.data['registrarFirstName'] = user.FirstName

            # Create the serializer
            serializer = ClientSerializer(data=request.data)

            if serializer.is_valid():
                # Save the client with the associated user and registrar
                client = serializer.save()

                # Make request.data immutable again
                request.data._mutable = False

                return Response({'message': 'Client registration successful', 'client_id': client.id})
            else:
                # Make request.data immutable again
                request.data._mutable = False

                return Response({'message': 'Client registration failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            # Make request.data immutable again
            request.data._mutable = False
            
            print(f"IntegrityError: {e}")
            return Response({'message': 'Client registration failed. Duplicate client.'}, status=status.HTTP_400_BAD_REQUEST)

    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None

        if file:
            folder = f"client_files/{request.data['firstName']}_{request.data['lastName']}"
            file_content = file.read()
            # file_checksum = request.data.get(f'{file_key}_checksum')

            if isinstance(file, InMemoryUploadedFile):
                file_link = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link, msg = upload_to_firebase_storage(folder, file_name, local_file_path)

            # print(f"{file_name.capitalize()} Link Before Saving:", file_link)
            return file_link, msg
        else:
            return None, f"No file found for {file_name} uploaded to"
    
    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None

        if file:
            folder = f"client_files/{request.data['firstName']}_{request.data['lastName']}"
            file_content = file.read()
            # file_checksum = request.data.get(f'{file_key}_checksum')

            if isinstance(file, InMemoryUploadedFile):
                file_link = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link, msg = upload_to_firebase_storage(folder, file_name, local_file_path)

            # print(f"{file_name.capitalize()} Link Before Saving:", file_link)
            return file_link, msg
        else:
            return None, f"No file found for {file_name} uploaded to"

class ClientDeleteView(APIView):
    """
    API view for deleting a client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: DELETE /client-registration/<int:client_id>/
    """
    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin]
    def delete(self, request, client_id):
        """Handle DELETE requests for client deletion."""
        try:
            client = Client.objects.get(id=client_id)
            client.delete()
            return Response({'message': 'Client deletion successful'}, status=status.HTTP_204_NO_CONTENT)
        except Client.DoesNotExist:
            return Response({'message': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
        




class UncompletedClientRegistrationView(APIView):
    """
    API view for registering a client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: POST, PUT, GET /client-registration/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handle GET requests to retrieve data."""
        user = request.user
        clients = UncompletedClient.objects.filter(user=user)
        serializer = UncompletedClientSerializer(clients, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Handle POST requests for client registration."""
        user = request.user
        request_data = request.data.copy()  # Create a mutable copy of request data
        request_data['user'] = user.UserID

        uploaded_files = {}

        # print('====> request_data: ', request_data)

        # Handle file uploads to Firebase Storage
        files_to_upload = [
            'signature_file', 'bankStatement_file', 'professionalReference_file', 'confirmationLetter_file',
            'custody_accounts_file', 'source_of_funds_file', 'payslips_file', 'due_diligence_file',
            'financial_statements_file', 'proof_of_ownership_file', 'lease_agreement_file', 'documentary_evidence_file',
            'bank_statement_proceeds_file', 'bank_statement_file', 'cdd_documents_file', 'bank_statements_file',
            'bank_statements_proceeds_file', 'notarised_documents_file', 'letter_from_donor_file',
            'donor_source_of_wealth_file', 'donor_bank_statement_file', 'letter_from_relevant_org_file',
            'lottery_bank_statement_file', 'creditor_agreement_file', 'creditor_cdd_file', 'creditor_bank_statement_file',
            'legal_document_file', 'notary_letter_file', 'executor_letter_file', 'loan_agreement_file',
            'loan_bank_statement_file', 'related_third_party_loan_agreement_file', 'related_third_party_cdd_file',
            'related_third_party_bank_statement_file', 'unrelated_third_party_loan_agreement_file',
            'unrelated_third_party_cdd_file', 'unrelated_third_party_bank_statement_file', 'signed_letter_from_notary_file',
            'property_contract_file', 'insurance_pay_out_file', 'retirement_annuity_fund_statement_file', 'passport_file',
            'utility_file', 'wealth_file', 'cv_file', 'funds_file', 'source_of_wealth_file', 'principals_identification_file',
            'shareholders_file', 'declaration_of_trust_file', 'certificate_of_registration_file', 'deed_of_retirement_file',
            'business_plan_file', 'registered_office_file', 'register_of_trustee_file', 'proof_of_source_of_funds_file',
            'proof_of_source_of_wealth_file', 'latest_accounts_or_bank_statements_file', 'licence_file',
            'certificate_of_incumbency_file', 'charter_file', 'latest_accounts_file',
            'identification_documents_of_the_principals_of_the_foundation_file'
        ]

        for file_key in files_to_upload:
            file = request.FILES.get(file_key)
            if file and file.size > 0:
            
                file_link, msg = self.handle_file_upload(request, file_key, file_key + '.pdf')
                if file_link and isinstance(file_link, str) and file_link.startswith('https://storage.googleapis.'):
                    link_key = file_key.replace('_file', '_link')
                    # Update request data with the new key-value pair
                    request_data[link_key] = file_link
                    uploaded_files[link_key] = file_link
                else:
                    return JsonResponse({'message': msg}, status=400)

        try:
            request_data.update({
                'registrarID': user.UserID,
                'registrarEmail': user.email,
                'registrarFirstName': user.FirstName
            })
            # print("\n\n\n<<<<<<<<request data: ", request_data)

            serializer = UncompletedClientSerializer(data=request_data)

            if serializer.is_valid():
                client = serializer.save()
                return Response({'message': 'Client registration successful', 'client_id': client.id})
            else:
                for file_link in uploaded_files.values():
                    delete_firebase_file(file_link)
                return JsonResponse({'message': 'Registration failed', 'errors': serializer.errors}, status=400)
        except IntegrityError as e:
            for file_link in uploaded_files.values():
                    delete_firebase_file(file_link)
            # print(f"IntegrityError: {e}")
            return JsonResponse({f'message': 'Client registration failed.'}, status=400)
    
    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None
        msg = None

        if file:
            folder = f"pending_registration_client_files/{request.data['firstName']}_{request.data['lastName']}"
            file_content = file.read()

            if isinstance(file, InMemoryUploadedFile):

                file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link, msg = upload_to_firebase_storage(folder, file_name, local_file_path)

            return file_link, msg
        else:
            return None, f"No file found for {file_name} uploaded to"


logger = logging.getLogger(__name__)
class UpdateUncompletedClientView(generics.UpdateAPIView):
    """
    API view for updating a client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: PUT /client-registration/<int:client_id>/
    """

    queryset = UncompletedClient.objects.all()
    serializer_class = UpdateUncompletedClientSerializer
    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin]
    lookup_field = 'id'

    def merge_expected_account_activity(self, existing_data, incoming_data):
        # Convert both existing and incoming data to dictionaries indexed by 'id' for easy comparison
        existing_dict = {item['id']: item for item in existing_data}
        incoming_dict = {item['id']: item for item in incoming_data}

        # Iterate through the existing data and update with incoming non-empty fields
        for key, existing_item in existing_dict.items():
            incoming_item = incoming_dict.get(key, {})
            for field in ['year1', 'year2', 'year3']:
                if incoming_item.get(field) not in [None, '']:
                    existing_item[field] = incoming_item[field]

        merged_data = list(existing_dict.values())
        # Print the merged data for debugging
        # print("Merged data:", merged_data)
        
        return merged_data

    def merge_financial_forecast(self, existing_data, incoming_data):
        if isinstance(existing_data, str):
            existing_data = json.loads(existing_data)
        if isinstance(incoming_data, str):
            incoming_data = json.loads(incoming_data)

        # Convert both existing and incoming data to dictionaries indexed by 'id' for easy comparison
        existing_dict = {item['id']: item for item in existing_data}
        incoming_dict = {item['id']: item for item in incoming_data}

        # Iterate through the existing data and update with incoming non-empty fields
        for key, existing_item in existing_dict.items():
            incoming_item = incoming_dict.get(key, {})
            for field in ['year1', 'year2', 'year3']:
                if incoming_item.get(field) not in [None, '']:
                    existing_item[field] = incoming_item[field]

        merged_data = list(existing_dict.values())
        # Print the merged data for debugging
        # print("Merged financial forecast data:", merged_data)
        
        return merged_data

    def perform_update(self, serializer):
        request = self.request
        request_data = request.data.copy()
        
        uploaded_files = {}
        files_to_upload = [
            'signature_file', 'bankStatement_file', 'professionalReference_file', 'confirmationLetter_file',
            'custody_accounts_file', 'source_of_funds_file', 'payslips_file', 'due_diligence_file',
            'financial_statements_file', 'proof_of_ownership_file', 'lease_agreement_file', 'documentary_evidence_file',
            'bank_statement_proceeds_file', 'bank_statement_file', 'cdd_documents_file', 'bank_statements_file',
            'bank_statements_proceeds_file', 'notarised_documents_file', 'letter_from_donor_file',
            'donor_source_of_wealth_file', 'donor_bank_statement_file', 'letter_from_relevant_org_file',
            'lottery_bank_statement_file', 'creditor_agreement_file', 'creditor_cdd_file', 'creditor_bank_statement_file',
            'legal_document_file', 'notary_letter_file', 'executor_letter_file', 'loan_agreement_file',
            'loan_bank_statement_file', 'related_third_party_loan_agreement_file', 'related_third_party_cdd_file',
            'related_third_party_bank_statement_file', 'unrelated_third_party_loan_agreement_file',
            'unrelated_third_party_cdd_file', 'unrelated_third_party_bank_statement_file', 'signed_letter_from_notary_file',
            'property_contract_file', 'insurance_pay_out_file', 'retirement_annuity_fund_statement_file', 'passport_file',
            'utility_file', 'wealth_file', 'cv_file', 'funds_file', 'source_of_wealth_file', 'principals_identification_file',
            'shareholders_file', 'declaration_of_trust_file', 'certificate_of_registration_file', 'deed_of_retirement_file',
            'business_plan_file', 'registered_office_file', 'register_of_trustee_file', 'proof_of_source_of_funds_file',
            'proof_of_source_of_wealth_file', 'latest_accounts_or_bank_statements_file', 'licence_file',
            'certificate_of_incumbency_file', 'charter_file', 'latest_accounts_file',
            'identification_documents_of_the_principals_of_the_foundation_file'
        ]

        for file_key in files_to_upload:
            file = request.FILES.get(file_key)
            if file and file.size > 0:
                file_link, msg = self.handle_file_upload(request, file_key, file_key + '.pdf')
                if file_link and isinstance(file_link, str) and file_link.startswith('https://storage.googleapis.'):
                    link_key = file_key.replace('_file', '_link')
                    request_data[link_key] = file_link
                    uploaded_files[link_key] = file_link
                else:
                    logger.error(f"File upload error: {msg}")
                    return JsonResponse({'message': msg}, status=400)

        instance = serializer.instance

        # Merge expectedAccountActivity
        existing_expected_account_activity = instance.expectedAccountActivity or []
        incoming_expected_account_activity = request_data.get('expectedAccountActivity', [])
        if isinstance(incoming_expected_account_activity, str):
            incoming_expected_account_activity = json.loads(incoming_expected_account_activity)
        merged_expected_account_activity = self.merge_expected_account_activity(
            existing_expected_account_activity, incoming_expected_account_activity
        )
        # Update the request data with the merged expectedAccountActivity
        request_data['expectedAccountActivity'] = merged_expected_account_activity

        # Merge financialForecast
        existing_financial_forecast = instance.financialForecast or []
        incoming_financial_forecast = request_data.get('financialForecast', [])
        if isinstance(incoming_financial_forecast, str):
            incoming_financial_forecast = json.loads(incoming_financial_forecast)
        merged_financial_forecast = self.merge_financial_forecast(
            existing_financial_forecast, incoming_financial_forecast
        )
        # Update the request data with the merged financialForecast
        request_data['financialForecast'] = merged_financial_forecast

        # Print the request data after merging for debugging
        # print("Request data after merging:", request_data)

        # Update only non-empty, non-null fields
        for field_name, value in request_data.items():
            if field_name == 'expectedAccountActivity':
                setattr(instance, field_name, merged_expected_account_activity)  # Set the merged data directly
            elif field_name == 'financialForecast':
                setattr(instance, field_name, merged_financial_forecast)  # Set the merged data directly
            elif value not in ["", None]:
                setattr(instance, field_name, value)

        # # Print the instance data before saving for debugging
        # print("Instance data before saving (expectedAccountActivity):", instance.expectedAccountActivity)
        # print("Instance data before saving (financialForecast):", instance.financialForecast)

        # Save the instance
        instance.save()

        # # Print the instance data after saving for debugging
        # print("Instance data after saving (expectedAccountActivity):", instance.expectedAccountActivity)
        # print("Instance data after saving (financialForecast):", instance.financialForecast)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                self.perform_update(serializer)
            return Response({'message': 'Client registration updated successfully'})
        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            return JsonResponse({'message': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error during the update process: {str(e)}")
            return JsonResponse({'message': 'An error occurred during the update process.'}, status=400)
    
    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None
        msg = None

        if file:
            folder = f"pending_registration_client_files/{request.data['firstName']}_{request.data['lastName']}"
            file_content = file.read()

            if isinstance(file, InMemoryUploadedFile):
                file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link, msg = upload_to_firebase_storage(folder, file_name, local_file_path)

            return file_link, msg
        else:
            return None, f"No file found for {file_name}"


class UncompletedClientDeleteView(APIView):
    """
    API view for deleting a incomplete client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: DELETE /client-registration/<int:client_id>/
    """
    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin]
    def delete(self, request, client_id):
        """Handle DELETE requests for client deletion."""
        try:
            client = UncompletedClient.objects.get(id=client_id)
            client.delete()
            return Response({'message': 'Client deletion successful'}, status=status.HTTP_204_NO_CONTENT)
        except UncompletedClient.DoesNotExist:
            return Response({'message': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)


class UncompletedClientDisoplayView(generics.RetrieveAPIView):
    queryset = UncompletedClient.objects.all()
    serializer_class = UncompletedClientSerializer
    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin]
    lookup_field = 'client_id'

    def retrieve(self, request, *args, **kwargs):
        client_id = kwargs.get('client_id')
        client = get_object_or_404(UncompletedClient, id=client_id)
        serializer = self.get_serializer(client)

        # Initialize files data dictionary
        files_data = {}

        # Download the files if the links exist
        file_fields = [
            'cv_link', 'national_id_link', 'signature_link', 'bankStatement_link', 
            'professionalReference_link', 'confirmationLetter_link', 'custody_accounts_link', 
            'source_of_funds_link', 'payslips_link', 'due_diligence_link', 'financial_statements_link', 
            'proof_of_ownership_link', 'lease_agreement_link', 'documentary_evidence_link', 
            'bank_statement_proceeds_link', 'bank_statement_link', 'cdd_documents_link', 
            'bank_statements_link', 'bank_statements_proceeds_link', 'notarised_documents_link', 
            'letter_from_donor_link', 'donor_source_of_wealth_link', 'donor_bank_statement_link', 
            'letter_from_relevant_org_link', 'lottery_bank_statement_link', 'creditor_agreement_link', 
            'creditor_cdd_link', 'creditor_bank_statement_link', 'legal_document_link', 'notary_letter_link', 
            'executor_letter_link', 'loan_agreement_link', 'loan_bank_statement_link', 
            'related_third_party_loan_agreement_link', 'related_third_party_cdd_link', 
            'related_third_party_bank_statement_link', 'unrelated_third_party_loan_agreement_link', 
            'unrelated_third_party_cdd_link', 'unrelated_third_party_bank_statement_link', 
            'signed_letter_from_notary_link', 'property_contract_link', 'insurance_pay_out_link', 
            'retirement_annuity_fund_statement_link', 'passport_link', 'utility_link', 'wealth_link', 
            'cv_link', 'funds_link', 'source_of_wealth_link', 'principals_identification_link', 
            'shareholders_link', 'declaration_of_trust_link', 'certificate_of_registration_link', 
            'deed_of_retirement_link', 'business_plan_link', 'registered_office_link', 'register_of_trustee_link', 
            'proof_of_source_of_funds_link', 'proof_of_source_of_wealth_link', 'latest_accounts_or_bank_statements_link', 
            'licence_link', 'certificate_of_incumbency_link', 'charter_link', 'latest_accounts_link', 
            'identification_documents_of_the_principals_of_the_foundation_link'
        ]

        for field in file_fields:
            link = getattr(client, field, None)
            if link:
                file_name, file_content = self.download_file_from_url(link)
                if file_content:
                    files_data[f'{field}_file'] = {
                        'file_name': file_name,
                        'file_content': base64.b64encode(file_content.getvalue()).decode('utf-8')
                    }

        # Combine client data and files data
        response_data = serializer.data
        response_data.update(files_data)

        return Response(response_data)

    def download_file_from_url(self, file_url):
        try:
            response = requests.get(file_url)
            if response.status_code == 200:
                file_name = unquote(os.path.basename(urlparse(file_url).path))
                file_content = BytesIO(response.content)
                return file_name, file_content
            else:
                return None, None
        except requests.RequestException as e:
            return None, None

class AllIncompleteClientsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handle GET requests to list all clients."""
        clients = UncompletedClient.objects.all()

        # Serialize the results
        serializer = UncompletedClientSerializer(clients, many=True)
        # print("===>", serializer.data)

        return Response(serializer.data)


class UncompletedClientByid(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the list of client IDs from the query parameters
        client_ids_str = self.request.query_params.get('ids', '')
        client_ids = [int(client_id) for client_id in client_ids_str.split(',') if client_id.isdigit()]
        # Filter and retrieve clients based on the provided IDs
        queryset = UncompletedClient.objects.filter(id__in=client_ids)
        return queryset

    def get(self, request, *args, **kwargs):
        """Handle GET requests to list all clients."""
        client_id = kwargs.get('client_id', None)
        if client_id is not None:
            client_ids = [client_id]
        else:
            client_ids_str = request.query_params.get('ids', '')
            client_ids = [int(client_id) for client_id in client_ids_str.split(',') if client_id.isdigit()]

        clients = UncompletedClient.objects.filter(id__in=client_ids)

        # Serialize the results
        serializer = ClientSerializer(clients, many=True)
        serialized_data = serializer.data

        # Initialize files data dictionary
        files_data = {}

        for client in clients:
            # Check and download the files for each client
            file_fields =[
            'cv_link', 'national_id_link', 'signature_link', 'bankStatement_link', 
            'professionalReference_link', 'confirmationLetter_link', 'custody_accounts_link', 
            'source_of_funds_link', 'payslips_link', 'due_diligence_link', 'financial_statements_link', 
            'proof_of_ownership_link', 'lease_agreement_link', 'documentary_evidence_link', 
            'bank_statement_proceeds_link', 'bank_statement_link', 'cdd_documents_link', 
            'bank_statements_link', 'bank_statements_proceeds_link', 'notarised_documents_link', 
            'letter_from_donor_link', 'donor_source_of_wealth_link', 'donor_bank_statement_link', 
            'letter_from_relevant_org_link', 'lottery_bank_statement_link', 'creditor_agreement_link', 
            'creditor_cdd_link', 'creditor_bank_statement_link', 'legal_document_link', 'notary_letter_link', 
            'executor_letter_link', 'loan_agreement_link', 'loan_bank_statement_link', 
            'related_third_party_loan_agreement_link', 'related_third_party_cdd_link', 
            'related_third_party_bank_statement_link', 'unrelated_third_party_loan_agreement_link', 
            'unrelated_third_party_cdd_link', 'unrelated_third_party_bank_statement_link', 
            'signed_letter_from_notary_link', 'property_contract_link', 'insurance_pay_out_link', 
            'retirement_annuity_fund_statement_link', 'passport_link', 'utility_link', 'wealth_link', 
            'cv_link', 'funds_link', 'source_of_wealth_link', 'principals_identification_link', 
            'shareholders_link', 'declaration_of_trust_link', 'certificate_of_registration_link', 
            'deed_of_retirement_link', 'business_plan_link', 'registered_office_link', 'register_of_trustee_link', 
            'proof_of_source_of_funds_link', 'proof_of_source_of_wealth_link', 'latest_accounts_or_bank_statements_link', 
            'licence_link', 'certificate_of_incumbency_link', 'charter_link', 'latest_accounts_link', 
            'identification_documents_of_the_principals_of_the_foundation_link'
        ]

            for field in file_fields:
                file_url = getattr(client, field, None)
                if file_url:
                    # print("file url in view is: ", file_url)
                    file_name, file_content = self.download_file_from_url(file_url)
                    if file_content:
                        files_data[f'{field.replace("_link", "_file")}'] = {
                            'file_name': file_name,
                            'file_content': base64.b64encode(file_content.getvalue()).decode('utf-8')
                        }

        # Combine serialized data and files data
        for client_data in serialized_data:
            client_id = client_data['id']
            for field in files_data:
                client_data[field] = files_data[field]

        return Response(serialized_data)

    def download_file_from_url(self, file_url):
        try:
            # print("downloading file.....")
            response = requests.get(file_url)
            if response.status_code == 200:
                file_name = unquote(os.path.basename(urlparse(file_url).path))
                file_content = BytesIO(response.content)
                # print("downloang file.....File name : ", file_name)
                return file_name, file_content
            else:
                return None, None
        except requests.RequestException as e:
            # print(f"Error during download: {e}")
            return None, None

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

