# views/client_views.py

from django.forms import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import ClientSerializer, UncompletedClientSerializer, UpdateUncompletedClientSerializer, UpdateClientSerializer
from ..models import Client, UncompletedClient
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from django.db import IntegrityError, transaction
from rest_framework import status
from django.utils import timezone
from ..helpers.firebase import upload_to_firebase_storage, delete_firebase_file, download_file_from_url
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..user_permissions import IsSuperuserOrManagerAdmin
from django.http import JsonResponse
import base64
from urllib.parse import unquote, urlparse
from io import BytesIO
import logging
import json
from django.utils.datastructures import MultiValueDictKeyError
from django.http import QueryDict
from rest_framework.parsers import MultiPartParser, FormParser


class ClientRegistrationView(APIView):

    """
    API view for registering a client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: POST /client-registration/
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        """Handle GET requests to retrieve data."""
        user = request.user
        clients = Client.objects.filter(user=user)
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Handle POST requests for client registration."""
        user = request.user
        has_multiple_files = False

        # Check for multiple files in the request
        # this for decision for copy or not copy
        if isinstance(request.data, QueryDict):
            for key in request.data.keys():
                values = request.data.getlist(key)
                if len(values) > 1 and any(isinstance(value, (str, bytes)) == False for value in values):
                    has_multiple_files = True
                    break

        # Decide whether to copy request.data
        if not has_multiple_files:
            request_data = request.data.copy()
        else:
            request_data = request.data
        
        request_data['user'] = user.UserID

        uploaded_files = {}

        try:
            request_data.update({
                'registrarID': user.UserID,
                'registrarEmail': user.email,
                'registrarFirstName': user.FirstName
            })

            serializer = ClientSerializer(data=request_data)

            if serializer.is_valid():
                client = serializer.save()

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
                    'identification_documents_of_the_principals_of_the_foundation_file', 'other_necessary_documents_file'
                ]

                for file_key in files_to_upload:
                    files = request.FILES.getlist(file_key)
                    if not files:  # Skip processing if no files are uploaded
                        print(f"No files uploaded for key: {file_key}")
                        continue
                    
                    file_links, msg = self.handle_multiple_file_upload(request, file_key, f"{client.id}-{file_key}")
                    if file_links:
                        link_key = file_key.replace('_file', '_link')
                        if len(file_links) == 1:
                            # Single file: add directly as a string
                            setattr(client, link_key, file_links[0])
                        else:
                            # Multiple files: encode as JSON array
                            setattr(client, link_key, json.dumps(file_links))
                        uploaded_files[link_key] = getattr(client, link_key)
                        print(f"File key: {file_key}, Uploaded files: {file_links}")
                    elif msg:
                        return JsonResponse({'message': f"Error processing file {file_key}: {msg}"}, status=400)

                # Save the client instance with updated file links
                client.save()

                # Serialize response with updated fields
                updated_serializer = ClientSerializer(client)

                return Response({'message': 'Client registration successful', 'client_id': client.id, 'data': updated_serializer.data, 'uploaded_files': uploaded_files})
            else:
                error_messages = " | ".join(
                    f"{field}: {', '.join(errors)}" for field, errors in serializer.errors.items()
                )
                for file_link in uploaded_files.values():
                    delete_firebase_file(file_link)
                return JsonResponse({'message': f'Registration failed: {error_messages}'}, status=400)
        except IntegrityError as e:
            print("integrity error: ", str(e))
            return JsonResponse({'message': 'Integrity Error', 'error': str(e)}, status=400)

    def handle_multiple_file_upload(self, request, file_key, prefix):
        """Handle multiple file uploads for a given key."""
        files = request.FILES.getlist(file_key)
        file_links = []
        msg = None  # Default message in case of no files or errors

        if files:
            for idx, file in enumerate(files):
                # Extract file extension and create a dynamic file name
                original_extension = file.name.split('.')[-1]
                file_name = f"{prefix}_{idx + 1}.{original_extension}"

                # Construct folder path dynamically
                folder = f"client_files/{request.data.get('firstName', 'Unknown')}_{request.data.get('lastName', 'Unknown')}_{request.data.get('tinNumber', 'Unknown_TinNumber')}"

                try:
                    # Handle file content
                    if isinstance(file, InMemoryUploadedFile):
                        file_content = file.read()
                        file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
                    else:
                        local_file_path = file.temporary_file_path()
                        with open(local_file_path, "rb") as temp_file:
                            file_content = temp_file.read()
                        file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)

                    # Append the link if upload succeeded
                    if file_link:
                        file_links.append(file_link)
                    else:
                        msg = f"Failed to upload file: {file.name}"
                        break

                except Exception as e:
                    msg = str(e)
                    break

        # Log the results for debugging
        print(f"File key: {file_key}, File links: {file_links}, Msg: {msg}")

        # Ensure consistent return
        if file_links:
            return file_links, None
        else:
            return None, msg or "No files uploaded."

    def delete_uncompleted_client(self, client_email):
        """Delete an uncompleted client with the same email if it exists."""
        try:
            uncompleted_client = UncompletedClient.objects.get(clientEmail=client_email)
            uncompleted_client.delete()
        except UncompletedClient.DoesNotExist:
            pass


class UpdateClientView(generics.UpdateAPIView):
    """
    API view for updating a client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: PUT /client-registration/<int:client_id>/
    """

    queryset = Client.objects.all()
    serializer_class = UpdateClientSerializer
    permission_classes = [IsAuthenticated, IsSuperuserOrManagerAdmin]
    lookup_field = 'id'

    def merge_expected_account_activity(self, existing_data, incoming_data):
        existing_dict = {item['id']: item for item in existing_data}
        incoming_dict = {item['id']: item for item in incoming_data}

        for key, existing_item in existing_dict.items():
            incoming_item = incoming_dict.get(key, {})
            for field in ['year1', 'year2', 'year3']:
                if incoming_item.get(field) not in [None, '']:
                    existing_item[field] = incoming_item[field]

        return list(existing_dict.values())

    def merge_financial_forecast(self, existing_data, incoming_data):
        if isinstance(existing_data, str):
            existing_data = json.loads(existing_data)
        if isinstance(incoming_data, str):
            incoming_data = json.loads(incoming_data)

        existing_dict = {item['id']: item for item in existing_data}
        incoming_dict = {item['id']: item for item in incoming_data}

        for key, existing_item in existing_dict.items():
            incoming_item = incoming_dict.get(key, {})
            for field in ['year1', 'year2', 'year3']:
                if incoming_item.get(field) not in [None, '']:
                    existing_item[field] = incoming_item[field]

        return list(existing_dict.values())

    def perform_update(self, serializer):
        request = self.request
        has_multiple_files = False

        if isinstance(request.data, QueryDict):
            for key in request.data.keys():
                values = request.data.getlist(key)
                if len(values) > 1 and any(not isinstance(value, (str, bytes)) for value in values):
                    has_multiple_files = True
                    break

        request_data = request.data if has_multiple_files else request.data.copy()

        uploaded_files = {}
        instance = serializer.instance
        client_id = instance.id

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
            files = request.FILES.getlist(file_key)
            if not files:
                continue

            file_links, msg = self.handle_multiple_file_upload(request, file_key, f"{client_id}-{file_key}")
            if file_links:
                link_key = file_key.replace('_file', '_link')
                if len(file_links) == 1:
                    request_data[link_key] = file_links[0]
                else:
                    request_data[link_key] = json.dumps(file_links)
                uploaded_files[link_key] = request_data[link_key]
            elif msg:
                raise ValueError(f"Error uploading {file_key}: {msg}")

        existing_expected_account_activity = instance.expectedAccountActivity or []
        incoming_expected_account_activity = request_data.get('expectedAccountActivity', [])
        if isinstance(incoming_expected_account_activity, str):
            incoming_expected_account_activity = json.loads(incoming_expected_account_activity)
        request_data['expectedAccountActivity'] = self.merge_expected_account_activity(
            existing_expected_account_activity, incoming_expected_account_activity
        )

        existing_financial_forecast = instance.financialForecast or []
        incoming_financial_forecast = request_data.get('financialForecast', [])
        if isinstance(incoming_financial_forecast, str):
            incoming_financial_forecast = json.loads(incoming_financial_forecast)
        request_data['financialForecast'] = self.merge_financial_forecast(
            existing_financial_forecast, incoming_financial_forecast
        )

        for field_name, value in request_data.items():
            if field_name in ['expectedAccountActivity', 'financialForecast']:
                setattr(instance, field_name, value)
            elif value not in ["", None]:
                setattr(instance, field_name, value)

        instance.save()

    def handle_multiple_file_upload(self, request, file_key, prefix):
        files = request.FILES.getlist(file_key)
        file_links = []
        msg = None

        for idx, file in enumerate(files):
            try:
                original_extension = file.name.split('.')[-1]
                file_name = f"{prefix}_{idx + 1}.{original_extension}"
                folder = f"client_files/{request.data.get('firstName', 'Unknown')}_{request.data.get('lastName', 'Unknown')}"

                if isinstance(file, InMemoryUploadedFile):
                    file_content = file.read()
                    file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
                else:
                    local_file_path = file.temporary_file_path()
                    with open(local_file_path, "rb") as temp_file:
                        file_content = temp_file.read()
                    file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)

                if file_link:
                    file_links.append(file_link)
            except Exception as e:
                msg = str(e)
                break

        return file_links, msg

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        try:
            serializer.is_valid(raise_exception=True)  # Validation occurs here
            print("Validation passed. Proceeding with update...")

            with transaction.atomic():
                self.perform_update(serializer)

            return Response({'message': 'Client updated successfully'})

        except serializer.ValidationError as e:
            # Debug: Log validation errors
            print("Validation error:", e.detail)
            return JsonResponse({'message': 'Validation failed', 'errors': e.detail}, status=400)

        except IntegrityError as e:
            error_message = f"Database integrity error: {str(e)}"
            print(error_message)
            return JsonResponse({'message': error_message}, status=400)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return JsonResponse({'message': error_message}, status=400)
        
        
    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None
        msg = None

        if file:
            folder = f"client_files/{request.data['firstName']}_{request.data['lastName']}"
            file_content = file.read()

            if isinstance(file, InMemoryUploadedFile):
                file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link, msg = upload_to_firebase_storage(folder, file_name, local_file_path)

            return file_link, msg
        else:
            return None, f"No file found for {file_name}"


    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None
        msg = None

        if file:
            folder = f"client_files/{request.data['firstName']}_{request.data['lastName']}"
            file_content = file.read()

            if isinstance(file, InMemoryUploadedFile):
                file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link, msg = upload_to_firebase_storage(folder, file_name, local_file_path)

            return file_link, msg
        else:
            return None, f"No file found for {file_name}"


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
    API view for registering a incomplete client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: POST, PUT, GET /client-registration/
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        """Handle GET requests to retrieve data."""
        user = request.user
        clients = UncompletedClient.objects.filter(user=user)
        serializer = UncompletedClientSerializer(clients, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Handle POST requests for incomplete client registration."""
        user = request.user
        has_multiple_files = False

        # Check for multiple files in the request
        if isinstance(request.data, QueryDict):
            for key in request.data.keys():
                values = request.data.getlist(key)
                if len(values) > 1 and any(isinstance(value, (str, bytes)) == False for value in values):
                    has_multiple_files = True
                    break

        # Decide whether to copy request.data
        if not has_multiple_files:
            request_data = request.data.copy()
        else:
            request_data = request.data
        request_data['user'] = user.UserID

        uploaded_files = {}

        try:
            request_data.update({
                'registrarID': user.UserID,
                'registrarEmail': user.email,
                'registrarFirstName': user.FirstName
            })

            serializer = UncompletedClientSerializer(data=request_data)

            if serializer.is_valid():
                client = serializer.save()

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
                    'identification_documents_of_the_principals_of_the_foundation_file', 'other_necessary_documents_file'
                ]

                for file_key in files_to_upload:
                    files = request.FILES.getlist(file_key)
                    if not files:  # Skip processing if no files are uploaded
                        print(f"No files uploaded for key: {file_key}")
                        continue
                    
                    file_links, msg = self.handle_multiple_file_upload(request, file_key, f"{client.id}-{file_key}")
                    if file_links:
                        link_key = file_key.replace('_file', '_link')
                        if len(file_links) == 1:
                            # Single file: add directly as a string
                            setattr(client, link_key, file_links[0])
                        else:
                            # Multiple files: encode as JSON array
                            setattr(client, link_key, json.dumps(file_links))
                        uploaded_files[link_key] = getattr(client, link_key)
                        print(f"File key: {file_key}, Uploaded files: {file_links}")
                    elif msg:
                        return JsonResponse({'message': f"Error processing file {file_key}: {msg}"}, status=400)

                # Save the client instance with updated file links
                client.save()

                # Serialize response with updated fields
                updated_serializer = UncompletedClientSerializer(client)

                return Response({'message': 'Temporary Client registration successful', 'client_id': client.id, 'data': updated_serializer.data, 'uploaded_files': uploaded_files})
            else:
                error_messages = " | ".join(
                    f"{field}: {', '.join(errors)}" for field, errors in serializer.errors.items()
                )
                for file_link in uploaded_files.values():
                    delete_firebase_file(file_link)
                return JsonResponse({'message': f'Registration failed: {error_messages}'}, status=400)
        except IntegrityError as e:
            print("integrity error: ", str(e))
            return JsonResponse({'message': 'Integrity Error', 'error': str(e)}, status=400)

    def handle_multiple_file_upload(self, request, file_key, prefix):
        """Handle multiple file uploads for a given key."""
        files = request.FILES.getlist(file_key)
        file_links = []
        msg = None  # Default message in case of no files or errors

        if files:
            for idx, file in enumerate(files):
                # Extract file extension and create a dynamic file name
                original_extension = file.name.split('.')[-1]
                file_name = f"{prefix}_{idx + 1}.{original_extension}"

                # Construct folder path dynamically
                folder = f"pending_registration_client_files/{request.data.get('firstName', 'Unknown')}_{request.data.get('lastName', 'Unknown')}_{request.data.get('tinNumber', 'Unknown_TinNumber')}"

                try:
                    # Handle file content
                    if isinstance(file, InMemoryUploadedFile):
                        file_content = file.read()
                        file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
                    else:
                        local_file_path = file.temporary_file_path()
                        with open(local_file_path, "rb") as temp_file:
                            file_content = temp_file.read()
                        file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)

                    # Append the link if upload succeeded
                    if file_link:
                        file_links.append(file_link)
                    else:
                        msg = f"Failed to upload file: {file.name}"
                        break

                except Exception as e:
                    msg = str(e)
                    break

        # Log the results for debugging
        print(f"File key: {file_key}, File links: {file_links}, Msg: {msg}")

        # Ensure consistent return
        if file_links:
            return file_links, None
        else:
            return None, msg or "No files uploaded."


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

        # Update only non-empty, non-null fields
        for field_name, value in request_data.items():
            if field_name == 'expectedAccountActivity':
                setattr(instance, field_name, merged_expected_account_activity)
            elif field_name == 'financialForecast':
                setattr(instance, field_name, merged_financial_forecast)
            elif value not in ["", None]:
                setattr(instance, field_name, value)

        # Save the instance
        instance.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    self.perform_update(serializer)
                # Return success message in response
                return JsonResponse({'message': 'Client registration updated successfully'}, status=200)
            except IntegrityError as e:
                logger.error(f"Database integrity error: {str(e)}")
                # Return a failure message in "message" field
                return JsonResponse({'message': 'Database integrity error occurred.'}, status=400)
            except Exception as e:
                logger.error(f"Error during the update process: {str(e)}")
                # Return a failure message in "message" field
                return JsonResponse({'message': 'An unexpected error occurred during the update process.'}, status=400)
        else:
            # If validation fails, include errors in "message" field
            errors = serializer.errors
            error_messages = "Validation failed: " + "; ".join([f"{field}: {', '.join(errors[field])}" for field in errors])
            return JsonResponse({'message': error_messages}, status=400)
    
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
                file_name, file_content = download_file_from_url(link)
                if file_content:
                    files_data[f'{field}_file'] = {
                        'file_name': file_name,
                        'file_content': base64.b64encode(file_content.getvalue()).decode('utf-8')
                    }

        # Combine client data and files data
        response_data = serializer.data
        response_data.update(files_data)

        return Response(response_data)


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
            'identification_documents_of_the_principals_of_the_foundation_link', 'other_necessary_documents_link'
        ]

            for field in file_fields:
                file_url = getattr(client, field, None)
                if file_url:
                    # print(f"Processing field: {field}, Value: {file_url}")  # Debugging print
                    # Handle single file link
                    if isinstance(file_url, str) and not file_url.startswith('['):
                        file_name, file_content = self.process_file_link(file_url)
                        if file_content:
                            # print(f"Downloaded file: {file_name}")
                            mapped_field = field.replace('_link', '_file')
                            files_data[mapped_field] = {
                                'file_name': file_name,
                                'file_content': base64.b64encode(file_content).decode('utf-8')
                            }

                    # Handle JSON array of file links
                    elif isinstance(file_url, list) or (isinstance(file_url, str) and file_url.startswith('[')):
                        try:
                            file_links = json.loads(file_url)
                            if isinstance(file_links, list):
                                # print(f"Found multiple links: {file_links}")  # Debugging print
                                file_metadata_list = []
                                for link in file_links:
                                    file_name, file_content = self.process_file_link(link)
                                    if file_content:
                                        # print(f"Downloaded file: {file_name}")  # Debugging print
                                        file_metadata_list.append({
                                            'file_name': file_name,
                                            'file_content': base64.b64encode(file_content).decode('utf-8')
                                        })
                                mapped_field = field.replace('_link', '_file')
                                files_data[mapped_field] = file_metadata_list
                        except json.JSONDecodeError:
                            print(f"Invalid JSON for field: {field}, Value: {file_url}")

        # Combine serialized data and files data
        for client_data in serialized_data:
            client_id = client_data['id']
            for field in files_data:
                client_data[field] = files_data[field]

        return Response(serialized_data)
    def process_file_link(self, file_url):
        """
        Download a file from the given URL and return its name and content.
        """
        try:
            # print(f"Attempting to download file from URL: {file_url}")  # Debugging print
            file_name, file_content = download_file_from_url(file_url)
            if isinstance(file_content, BytesIO):
                file_content = file_content.read()
            return file_name, file_content
        except Exception as e:
            # Log error if download fails
            print(f"Error processing file URL {file_url}: {e}")
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
        'id': 'id',
        'firstName': 'First Name',
        'lastName': 'Last Name',
        'taxResidency': 'Tax Residency',
        'tinNumber': 'TIN Number',
        'citizenship': 'Citizenship',
        'birthDate': 'Birth Date',
        'countryOfResidence': 'Country of Residence',
        'passportIdNumber': 'Passport ID Number',
        'countryOfIssue': 'Country of Issue',
        'NameOfEntity': 'Name of Entity',
        'PrevNameOfEntity': 'Previous Name of Entity',
        'TypeOfEntity': 'Type of Entity',
        'TypeOfLicense': 'Type of License',
        'sharePercent': 'Share Percentage',
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
        'NationalID': 'National ID',
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
        'CathegoryOfEntity': 'Category of Entity',
        'SPVType': 'SPV Type',
        'SectorOfEntity': 'Sector of Entity',
        'OtherSectorOfEntity': 'Other Sector of Entity',
        'isPep': 'Is PEP(Policy Exposed Person)',
        'incorporationDate': 'Incorporation Date',
        'countryOfIncorporation': 'Country of Incorporation',
        'registeredOfficeAddress': 'Registered Office Address',
        'businessActivity': 'Business Activity',
        'countryOfOperation': 'Country of Operation',
        'changeName': 'Changed Name?',
        'similarApplicationDetailsName': 'Former Name',
        'financialServicesBusiness': 'Carries out financial services else?',
        'jurisdictionName': 'Jurisdiction Name',
        'jurisdictionAddress': 'Jurisdiction Address',
        'similarApplication': 'Made Similar Application in Other Jurisdiction?',
        'similarApplicationDetailsPartner': 'Partner in Similar Application',
        'criticised': 'Criticised, Cencured, Displined, Suspended, or Fined by Regulatory Body?',
        'similarApplicationDetailsJurisdictions': 'Details of Criticism, Censure, Discipline, Suspension, or Fine',
        'bankruptcyApplication': 'Bankruptcy or Seisure Of Properties?',
        'similarApplicationDetailsForfeit': 'Details of Bankruptcy or Seisure Of Properties',
        'receiverAppointed': 'Administrator appointed or failed to satisfy a debt?',
        'similarApplicationDetailsReceiver': 'Details of Administrator appointed or failed to satisfy a debt',
        'civilProceedings': 'Civil Proceedings ?',
        'similarApplicationDetailsFinancial': 'Details of Civil Proceedings',
        'convicted': 'Convicted of any Offence?',
        'similarApplicationDetailsOffence': 'Details of Conviction',
        'directorConvicted': 'Director Convicted of any Offence?',
        'similarApplicationDetailsDirector': 'Details of Director Conviction',
        'RemittingParty': 'Remitting Party',
        'ModeOfPayment': 'Mode Of Payment',
        'RelationshipWithApplicant': 'Relationship With Applicant',
        'ProposedNameOption1': 'Proposed Name Option 1',
        'ProposedNameOption2': 'Proposed Name Option 2',
        'ProposedNameOption3': 'Proposed Name Option 3',
        'proposedActivity': 'Proposed Activity',
        'targetSectors': 'Target Sectors',
        'targetedCountries': 'Targeted Countries',
        'specialLicense': 'Special License?',
        'secretary': 'Secretary',
        'productService': 'Product Service',
        'businessAddress': 'Business Address',
        'sharesType': 'Shares Type',
        'sharesNumber': 'Shares Number',
        'statedCapital': 'Stated Capital',
        'sourceOfFunds': 'Source of Funds',
        'otherSourceOfFunds': 'Other Source of Funds',
        'countrySourceFunds': 'Country Source of Funds',
        'netAnnualIncome': 'Net Annual Income',
        'estimatedNetWorth': 'Estimated Net Worth',
        'sourceOfWealth': 'Source of Wealth',
        'otherSourceOfWealth': 'Other Source of Wealth',
        'countrySourceWealth': 'Country Source of Wealth',
        'bankInvolvedWealth': 'Bank Involved in Wealth',
        'isMlDirectors': 'Officers of ML Corporate Services act as Director?',
        'Director1FirstName': 'Director 1 First Name',
        'Director1LastName': 'Director 1 Last Name',
        'Director1email': 'Director 1 Email',
        'Director1contact': 'Director 1 Contact',
        'Director1BirthDate': 'Director 1 Birth Date',
        'Director1NationalID': 'Director 1 National ID',
        'Director1passportIdNumber': 'Director 1 Passport ID Number',
        'Director1countryOfIssue': 'Director 1 Country of Issue',
        'Director1passportExpiryDate': 'Director 1 Passport Expiry Date',
        'Director1citizenship': 'Director 1 Citizenship',
        'Director1specifiedCitizenship': 'Director 1 Specified Citizenship',
        'Director1countryOfResidence': 'Director 1 Country of Residence',
        'Director1preferredLanguage': 'Director 1 Preferred Language',
        'Director1NameOfEntity': 'Director 1 Name of Entity',
        'Director1tinNumber': 'Director 1 TIN Number',
        'Director1taxResidency': 'Director 1 Tax Residency',
        'Director1isPep': 'Director 1 is PEP',
        'Director2FirstName': 'Director 2 First Name',
        'Director2LastName': 'Director 2 Last Name',
        'Director2email': 'Director 2 Email',
        'Director2contact': 'Director 2 Contact',
        'Director2BirthDate': 'Director 2 Birth Date',
        'Director2NationalID': 'Director 2 National ID',
        'Director2passportIdNumber': 'Director 2 Passport ID Number',
        'Director2countryOfIssue': 'Director 2 Country of Issue',
        'Director2passportExpiryDate': 'Director 2 Passport Expiry Date',
        'Director2citizenship': 'Director 2 Citizenship',
        'Director2specifiedCitizenship': 'Director 2 Specified Citizenship',
        'Director2countryOfResidence': 'Director 2 Country of Residence',
        'Director2preferredLanguage': 'Director 2 Preferred Language',
        'Director2NameOfEntity': 'Director 2 Name of Entity',
        'Director2tinNumber': 'Director 2 TIN Number',
        'Director2taxResidency': 'Director 2 Tax Residency',
        'Director2isPep': 'Director 2 is PEP',
        'Director3FirstName': 'Director 3 First Name',
        'Director3LastName': 'Director 3 Last Name',
        'Director3email': 'Director 3 Email',
        'Director3contact': 'Director 3 Contact',
        'Director3BirthDate': 'Director 3 Birth Date',
        'Director3NationalID': 'Director 3 National ID',
        'Director3passportIdNumber': 'Director 3 Passport ID Number',
        'Director3countryOfIssue': 'Director 3 Country of Issue',
        'Director3passportExpiryDate': 'Director 3 Passport Expiry Date',
        'Director3citizenship': 'Director 3 Citizenship',
        'Director3specifiedCitizenship': 'Director 3 Specified Citizenship',
        'Director3countryOfResidence': 'Director 3 Country of Residence',
        'Director3preferredLanguage': 'Director 3 Preferred Language',
        'Director3NameOfEntity': 'Director 3 Name of Entity',
        'Director3tinNumber': 'Director 3 TIN Number',
        'Director3taxResidency': 'Director 3 Tax Residency',
        'Director3isPep': 'Director 3 is PEP',
        'bankName': 'Bank Name',
        'Currency': 'Currency',
        'groupASignatory1': 'Group A Signatory 1',
        'groupASignatory2': 'Group A Signatory 2',
        'groupASignatory3': 'Group A Signatory 3',
        'groupASignatory4': 'Group A Signatory 4',
        'groupBSignatory1': 'Group B Signatory 1',
        'groupBSignatory2': 'Group B Signatory 2',
        'groupBSignatory3': 'Group B Signatory 3',
        'groupBSignatory4': 'Group B Signatory 4',
        'authorizedUser1': 'Authorized User 1',
        'authorizedUser1AccessRights': 'Authorized User 1 Access Rights',
        'authorizedUser2': 'Authorized User 2',
        'authorizedUser2AccessRights': 'Authorized User 2 Access Rights',
        'authorizedUser3': 'Authorized User 3',
        'authorizedUser3AccessRights': 'Authorized User 3 Access Rights',
        'authorizedUser4': 'Authorized User 4',
        'authorizedUser4AccessRights': 'Authorized User 4 Access Rights',
        'modeOfOperation': 'Mode of Operation',
        'callBackProcessContact': 'Call Back Process Contact',
        'nameOfProposedOfficer': 'Name of Proposed Officer',
        'financialForecast': 'Financial Forecast',
        'expectedAccountActivity': 'Expected Account Activity',
    }

    file_fields = [
        'registration_certificate_link', 'signature_link', 'bankStatement_link', 'professionalReference_link', 'national_id_link',
        'passport_link', 'cv_link', 'source_of_funds_link', 'payslips_link', 'due_diligence_link', 'financial_statements_link',
        'proof_of_ownership_link', 'lease_agreement_link', 'documentary_evidence_link', 'bank_statement_proceeds_link', 'bank_statement_link',
        'cdd_documents_link', 'bank_statements_link', 'bank_statements_proceeds_link', 'notarised_documents_link', 'letter_from_donor_link',
        'donor_source_of_wealth_link', 'donor_bank_statement_link', 'letter_from_relevant_org_link', 'lottery_bank_statement_link',
        'creditor_agreement_link', 'creditor_cdd_link', 'creditor_bank_statement_link', 'legal_document_link', 'notary_letter_link',
        'executor_letter_link', 'loan_agreement_link', 'loan_bank_statement_link', 'related_third_party_loan_agreement_link',
        'related_third_party_cdd_link', 'related_third_party_bank_statement_link', 'unrelated_third_party_loan_agreement_link',
        'unrelated_third_party_cdd_link', 'unrelated_third_party_bank_statement_link', 'signed_letter_from_notary_link', 'property_contract_link',
        'insurance_pay_out_link', 'retirement_annuity_fund_statement_link', 'utility_link', 'wealth_link', 'funds_link', 'source_of_wealth_link',
        'principals_identification_link', 'shareholders_link', 'declaration_of_trust_link', 'certificate_of_registration_link', 'deed_of_retirement_link',
        'business_plan_link', 'registered_office_link', 'register_of_trustee_link', 'proof_of_source_of_funds_link', 'proof_of_source_of_wealth_link',
        'latest_accounts_or_bank_statements_link', 'licence_link', 'certificate_of_incumbency_link', 'charter_link', 'latest_accounts_link',
        'identification_documents_of_the_principals_of_the_foundation_link', 'other_necessary_documents_link'
    ]

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

        # Iterate through provided client IDs
        for client_id in [int(client_id) for client_id in self.request.query_params.get('ids', '').split(',')]:
            client = get_object_or_404(queryset, id=client_id)
            serializer = ClientSerializer(client)
            serialized_data = serializer.data

            # Rename keys based on the display names map
            renamed_data = {
                self.display_names_map.get(key, key): value
                for key, value in serialized_data.items()
                if key in self.display_names_map
            }

            # Check and handle files for each client
            for field in self.file_fields:
                file_field_value = getattr(client, field, None)
                if file_field_value:
                    # print(f"Processing field: {field}, Value: {file_field_value}")  # Debugging print
                    # Handle single file link
                    if isinstance(file_field_value, str) and not file_field_value.startswith('['):
                        file_name, file_content = self.process_file_link(file_field_value)
                        if file_content:
                            # print(f"Downloaded file: {file_name}")  # Debugging print
                            mapped_field = field.replace('_link', '_file').replace('_', ' ')
                            renamed_data[mapped_field] = {
                                'file_name': file_name,
                                'file_content': base64.b64encode(file_content).decode('utf-8')
                            }

                    # Handle JSON array of file links
                    elif isinstance(file_field_value, str) and file_field_value.startswith('['):
                        try:
                            file_links = json.loads(file_field_value)
                            if isinstance(file_links, list):
                                # print(f"Found multiple links: {file_links}")  # Debugging print
                                file_metadata_list = []
                                for link in file_links:
                                    file_name, file_content = self.process_file_link(link)
                                    if file_content:
                                        # print(f"Downloaded file: {file_name}")  # Debugging print
                                        file_metadata_list.append({
                                            'file_name': file_name,
                                            'file_content': base64.b64encode(file_content).decode('utf-8')
                                        })
                                mapped_field = field.replace('_link', '_files').replace('_', ' ')
                                renamed_data[mapped_field] = file_metadata_list
                        except json.JSONDecodeError:
                            print(f"Invalid JSON for field: {field}, Value: {file_field_value}")  # Debugging print

            serialized_clients.append(renamed_data)

        return Response(serialized_clients)


    def process_file_link(self, file_url):
        """
        Download a file from the given URL and return its name and content.
        """
        try:
            print(f"Attempting to download file from URL: {file_url}")  # Debugging print
            file_name, file_content = download_file_from_url(file_url)
            if isinstance(file_content, BytesIO):
                file_content = file_content.read()
            return file_name, file_content
        except Exception as e:
            # Log error if download fails
            print(f"Error processing file URL {file_url}: {e}")
            return None, None

class ClientByIdListModificationView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the list of client IDs from the query parameters
        client_ids_str = self.request.query_params.get('ids', '')
        client_ids = [int(client_id) for client_id in client_ids_str.split(',') if client_id.isdigit()]
        # Filter and retrieve clients based on the provided IDs
        queryset = Client.objects.filter(id__in=client_ids)
        return queryset

    def get(self, request, *args, **kwargs):
        """Handle GET requests to list all clients."""
        client_id = kwargs.get('client_id', None)
        if client_id is not None:
            client_ids = [client_id]
        else:
            client_ids_str = request.query_params.get('ids', '')
            client_ids = [int(client_id) for client_id in client_ids_str.split(',') if client_id.isdigit()]

        clients = Client.objects.filter(id__in=client_ids)

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
            'identification_documents_of_the_principals_of_the_foundation_link', 'other_necessary_documents_link'
        ]

            for field in file_fields:
                file_url = getattr(client, field, None)
                if file_url:
                    # print(f"Processing field: {field}, Value: {file_url}")  # Debugging print
                    # Handle single file link
                    if isinstance(file_url, str) and not file_url.startswith('['):
                        file_name, file_content = self.process_file_link(file_url)
                        if file_content:
                            # print(f"Downloaded file: {file_name}")
                            mapped_field = field.replace('_link', '_file')
                            files_data[mapped_field] = {
                                'file_name': file_name,
                                'file_content': base64.b64encode(file_content).decode('utf-8')
                            }

                    # Handle JSON array of file links
                    elif isinstance(file_url, list) or (isinstance(file_url, str) and file_url.startswith('[')):
                        try:
                            file_links = json.loads(file_url)
                            if isinstance(file_links, list):
                                # print(f"Found multiple links: {file_links}")  # Debugging print
                                file_metadata_list = []
                                for link in file_links:
                                    file_name, file_content = self.process_file_link(link)
                                    if file_content:
                                        # print(f"Downloaded file: {file_name}")  # Debugging print
                                        file_metadata_list.append({
                                            'file_name': file_name,
                                            'file_content': base64.b64encode(file_content).decode('utf-8')
                                        })
                                mapped_field = field.replace('_link', '_file')
                                files_data[mapped_field] = file_metadata_list
                        except json.JSONDecodeError:
                            print(f"Invalid JSON for field: {field}, Value: {file_url}")

        # Combine serialized data and files data
        for client_data in serialized_data:
            client_id = client_data['id']
            for field in files_data:
                client_data[field] = files_data[field]

        return Response(serialized_data)
    
    def process_file_link(self, file_url):
        """
        Download a file from the given URL and return its name and content.
        """
        try:
            # print(f"Attempting to download file from URL: {file_url}")  # Debugging print
            file_name, file_content = download_file_from_url(file_url)
            if isinstance(file_content, BytesIO):
                file_content = file_content.read()
            return file_name, file_content
        except Exception as e:
            # Log error if download fails
            print(f"Error processing file URL {file_url}: {e}")
            return None, None
