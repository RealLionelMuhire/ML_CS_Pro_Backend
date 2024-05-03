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
from ..helpers.firebase import upload_to_firebase_storage, download_file_from_url
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
        # print(request)
        user = request.user

        # Combine the user data with the client data
        request_data = request.data
        request_data['user'] = user.UserID

        # Handle file uploads to Firebase Storage
        signature_link = self.handle_file_upload(request, 'signature_file', 'signature.pdf')
        bankStatement_link = self.handle_file_upload(request, 'bankStatement_file', 'bankStatement.pdf')
        professionalReference_link = self.handle_file_upload(request, 'professionalReference_file', 'professionalReference.pdf')

    #     confirmationLetter_file: createFileSchema(),
    # custody_accounts_file: createFileSchema(),
    # source_of_funds_file: createFileSchema(),
    # payslips_file: createFileSchema(),
    # due_diligence_file: createFileSchema(),
    # financial_statements_file: createFileSchema(),
    # proof_of_ownership_file: createFileSchema(),
    # lease_agreement_file: createFileSchema(),
    # documentary_evidence_file: createFileSchema(),
    # bank_statement_proceeds_file: createFileSchema(),
    # bank_statement_file: createFileSchema(),
    # cdd_documents_file: createFileSchema(),
    # bank_statements_file: createFileSchema(),
    # bank_statements_proceeds_file: createFileSchema(),

        confirmationLetter_link = self.handle_file_upload(request, 'confirmationLetter_file', 'confirmationLetter.pdf')
        custody_accounts_link = self.handle_file_upload(request, 'custody_accounts_file', 'custody_accounts.pdf')
        source_of_funds_link = self.handle_file_upload(request, 'source_of_funds_file', 'source_of_funds.pdf')
        payslips_link = self.handle_file_upload(request, 'payslips_file', 'payslips.pdf')
        due_diligence_link = self.handle_file_upload(request, 'due_diligence_file', 'due_diligence.pdf')
        financial_statements_link = self.handle_file_upload(request, 'financial_statements_file', 'financial_statements.pdf')
        proof_of_ownership_link = self.handle_file_upload(request, 'proof_of_ownership_file', 'proof_of_ownership.pdf')
        lease_agreement_link = self.handle_file_upload(request, 'lease_agreement_file', 'lease_agreement.pdf')
        documentary_evidence_link = self.handle_file_upload(request, 'documentary_evidence_file', 'documentary_evidence.pdf')
        bank_statement_proceeds_link = self.handle_file_upload(request, 'bank_statement_proceeds_file', 'bank_statement_proceeds.pdf')
        bank_statement_link = self.handle_file_upload(request, 'bank_statement_file', 'bank_statement.pdf')
        cdd_documents_link = self.handle_file_upload(request, 'cdd_documents_file', 'cdd_documents.pdf')
        bank_statements_link = self.handle_file_upload(request, 'bank_statements_file', 'bank_statements.pdf')
        bank_statements_proceeds_link = self.handle_file_upload(request, 'bank_statements_proceeds_file', 'bank_statements_proceeds.pdf')

    #     notarised_documents_file: createFileSchema(),
    # letter_from_donor_file: createFileSchema(),
    # donor_source_of_wealth_file: createFileSchema(),
    # donor_bank_statement_file: createFileSchema(),
    # letter_from_relevant_org_file: createFileSchema(),
    # lottery_bank_statement_file: createFileSchema(),
    # creditor_agreement_file: createFileSchema(),
    # creditor_cdd_file: createFileSchema(),
    # creditor_bank_statement_file: createFileSchema(),
    # legal_document_file: createFileSchema(),
    # notary_letter_file: createFileSchema(),
    # executor_letter_file: createFileSchema(),
    # loan_agreement_file: createFileSchema(),
    # loan_bank_statement_file: createFileSchema(),
    # related_third_party_loan_agreement_file: createFileSchema(),
    # related_third_party_cdd_file: createFileSchema(),
    # related_third_party_bank_statement_file: createFileSchema(),
    # unrelated_third_party_loan_agreement_file: createFileSchema(),
    # unrelated_third_party_cdd_file: createFileSchema(),
    # unrelated_third_party_bank_statement_file: createFileSchema(),
    # signed_letter_from_notary_file: createFileSchema(),
    # property_contract_file: createFileSchema(),
    # insurance_pay_out_file: createFileSchema(),
    # retirement_annuity_fund_statement_file: createFileSchema(),

        notarised_documents_link = self.handle_file_upload(request, 'notarised_documents_file', 'notarised_documents.pdf')
        letter_from_donor_link = self.handle_file_upload(request, 'letter_from_donor_file', 'letter_from_donor.pdf')
        donor_source_of_wealth_link = self.handle_file_upload(request, 'donor_source_of_wealth_file', 'donor_source_of_wealth.pdf')
        donor_bank_statement_link = self.handle_file_upload(request, 'donor_bank_statement_file', 'donor_bank_statement.pdf')
        letter_from_relevant_org_link = self.handle_file_upload(request, 'letter_from_relevant_org_file', 'letter_from_relevant_org.pdf')
        lottery_bank_statement_link = self.handle_file_upload(request, 'lottery_bank_statement_file', 'lottery_bank_statement.pdf')
        creditor_agreement_link = self.handle_file_upload(request, 'creditor_agreement_file', 'creditor_agreement.pdf')
        creditor_cdd_link = self.handle_file_upload(request, 'creditor_cdd_file', 'creditor_cdd.pdf')
        creditor_bank_statement_link = self.handle_file_upload(request, 'creditor_bank_statement_file', 'creditor_bank_statement.pdf')
        legal_document_link = self.handle_file_upload(request, 'legal_document_file', 'legal_document.pdf')
        notary_letter_link = self.handle_file_upload(request, 'notary_letter_file', 'notary_letter.pdf')
        executor_letter_link = self.handle_file_upload(request, 'executor_letter_file', 'executor_letter.pdf')
        loan_agreement_link = self.handle_file_upload(request, 'loan_agreement_file', 'loan_agreement.pdf')
        loan_bank_statement_link = self.handle_file_upload(request, 'loan_bank_statement_file', 'loan_bank_statement.pdf')
        related_third_party_loan_agreement_link = self.handle_file_upload(request, 'related_third_party_loan_agreement_file', 'related_third_party_loan_agreement.pdf')
        related_third_party_cdd_link = self.handle_file_upload(request, 'related_third_party_cdd_file', 'related_third_party_cdd.pdf')
        related_third_party_bank_statement_link = self.handle_file_upload(request, 'related_third_party_bank_statement_file', 'related_third_party_bank_statement.pdf')
        unrelated_third_party_loan_agreement_link = self.handle_file_upload(request, 'unrelated_third_party_loan_agreement_file', 'unrelated_third_party_loan_agreement.pdf')
        unrelated_third_party_cdd_link = self.handle_file_upload(request, 'unrelated_third_party_cdd_file', 'unrelated_third_party_cdd.pdf')
        unrelated_third_party_bank_statement_link = self.handle_file_upload(request, 'unrelated_third_party_bank_statement_file', 'unrelated_third_party_bank_statement.pdf')
        signed_letter_from_notary_link = self.handle_file_upload(request, 'signed_letter_from_notary_file', 'signed_letter_from_notary.pdf')
        property_contract_link = self.handle_file_upload(request, 'property_contract_file', 'property_contract.pdf')
        insurance_pay_out_link = self.handle_file_upload(request, 'insurance_pay_out_file', 'insurance_pay_out.pdf')
        retirement_annuity_fund_statement_link = self.handle_file_upload(request, 'retirement_annuity_fund_statement_file', 'retirement_annuity_fund_statement.pdf')

    #     passport_file: createFileSchema(),
    # utility_file: createFileSchema(),
    # wealth_file: createFileSchema(),
    # cv_file: createFileSchema(),
    # funds_file: createFileSchema(),
    # source_of_wealth_file: createFileSchema(),
    # financialStatements_file: createFileSchema(),
    # principals_identification_file: createFileSchema(),
    # shareholders_file: createFileSchema(),
    # declaration_of_trust_file: createFileSchema(),
    # certificate_of_registration_file: createFileSchema(),
    # deed_of_retirement_file: createFileSchema(),
    # business_plan_file: createFileSchema(),
    # registered_office_file: createFileSchema(),
    # register_of_trustee_file: createFileSchema(),
    # proof_of_source_of_funds_file: createFileSchema(),
    # proof_of_source_of_wealth_file: createFileSchema(),
    # latest_accounts_or_bank_statements_file: createFileSchema(),
    # licence_file: createFileSchema(),
    # certificate_of_incumbency_file: createFileSchema(),
    # charter_file: createFileSchema(),
    # latest_accounts_file: createFileSchema(),
    # identification_documents_of_the_principals_of_the_foundation_file:
    #   createFileSchema(),

        passport_link = self.handle_file_upload(request, 'passport_file', 'passport.pdf')
        utility_link = self.handle_file_upload(request, 'utility_file', 'utility.pdf')
        wealth_link = self.handle_file_upload(request, 'wealth_file', 'wealth.pdf')
        cv_link = self.handle_file_upload(request, 'cv_file', 'cv.pdf')
        funds_link = self.handle_file_upload(request, 'funds_file', 'funds.pdf')
        source_of_wealth_link = self.handle_file_upload(request, 'source_of_wealth_file', 'source_of_wealth.pdf')
        principals_identification_link = self.handle_file_upload(request, 'principals_identification_file', 'principals_identification.pdf')
        shareholders_link = self.handle_file_upload(request, 'shareholders_file', 'shareholders.pdf')
        declaration_of_trust_link = self.handle_file_upload(request, 'declaration_of_trust_file', 'declaration_of_trust.pdf')
        certificate_of_registration_link = self.handle_file_upload(request, 'certificate_of_registration_file', 'certificate_of_registration.pdf')
        deed_of_retirement_link = self.handle_file_upload(request, 'deed_of_retirement_file', 'deed_of_retirement.pdf')
        business_plan_link = self.handle_file_upload(request, 'business_plan_file', 'business_plan.pdf')
        registered_office_link = self.handle_file_upload(request, 'registered_office_file', 'registered_office.pdf')
        register_of_trustee_link = self.handle_file_upload(request, 'register_of_trustee_file', 'register_of_trustee.pdf')
        proof_of_source_of_funds_link = self.handle_file_upload(request, 'proof_of_source_of_funds_file', 'proof_of_source_of_funds.pdf')
        proof_of_source_of_wealth_link = self.handle_file_upload(request, 'proof_of_source_of_wealth_file', 'proof_of_source_of_wealth.pdf')
        latest_accounts_or_bank_statements_link = self.handle_file_upload(request, 'latest_accounts_or_bank_statements_file', 'latest_accounts_or_bank_statements.pdf')
        licence_link = self.handle_file_upload(request, 'licence_file', 'licence.pdf')
        certificate_of_incumbency_link = self.handle_file_upload(request, 'certificate_of_incumbency_file', 'certificate_of_incumbency.pdf')
        charter_link = self.handle_file_upload(request, 'charter_file', 'charter.pdf')
        latest_accounts_link = self.handle_file_upload(request, 'latest_accounts_file', 'latest_accounts.pdf')
        identification_documents_of_the_principals_of_the_foundation_link = self.handle_file_upload(request, 'identification_documents_of_the_principals_of_the_foundation_file', 'identification_documents_of_the_principals_of_the_foundation.pdf')

        # Update the request data with the obtained links
        request.data.update({
            'signature_link': signature_link,
            'bankStatement_link': bankStatement_link,
            'professionalReference_link': professionalReference_link,
            'confirmationLetter_link': confirmationLetter_link,
            'custody_accounts_link': custody_accounts_link,
            'source_of_funds_link': source_of_funds_link,
            'payslips_link': payslips_link,
            'due_diligence_link': due_diligence_link,
            'financial_statements_link': financial_statements_link,
            'proof_of_ownership_link': proof_of_ownership_link,
            'lease_agreement_link': lease_agreement_link,
            'documentary_evidence_link': documentary_evidence_link,
            'bank_statement_proceeds_link': bank_statement_proceeds_link,
            'bank_statement_link': bank_statement_link,
            'cdd_documents_link': cdd_documents_link,
            'bank_statements_link': bank_statements_link,
            'bank_statements_proceeds_link': bank_statements_proceeds_link,
            'notarised_documents_link': notarised_documents_link,
            'letter_from_donor_link': letter_from_donor_link,
            'donor_source_of_wealth_link': donor_source_of_wealth_link,
            'donor_bank_statement_link': donor_bank_statement_link,
            'letter_from_relevant_org_link': letter_from_relevant_org_link,
            'lottery_bank_statement_link': lottery_bank_statement_link,
            'creditor_agreement_link': creditor_agreement_link,
            'creditor_cdd_link': creditor_cdd_link,
            'creditor_bank_statement_link': creditor_bank_statement_link,
            'legal_document_link': legal_document_link,
            'notary_letter_link': notary_letter_link,
            'executor_letter_link': executor_letter_link,
            'loan_agreement_link': loan_agreement_link,
            'loan_bank_statement_link': loan_bank_statement_link,
            'related_third_party_loan_agreement_link': related_third_party_loan_agreement_link,
            'related_third_party_cdd_link': related_third_party_cdd_link,
            'related_third_party_bank_statement_link': related_third_party_bank_statement_link,
            'unrelated_third_party_loan_agreement_link': unrelated_third_party_loan_agreement_link,
            'unrelated_third_party_cdd_link': unrelated_third_party_cdd_link,
            'unrelated_third_party_bank_statement_link': unrelated_third_party_bank_statement_link,
            'signed_letter_from_notary_link': signed_letter_from_notary_link,
            'property_contract_link': property_contract_link,
            'insurance_pay_out_link': insurance_pay_out_link,
            'retirement_annuity_fund_statement_link': retirement_annuity_fund_statement_link,
            'passport_link': passport_link,
            'utility_link': utility_link,
            'wealth_link': wealth_link,
            'cv_link': cv_link,
            'funds_link': funds_link,
            'source_of_wealth_link': source_of_wealth_link,
            'principals_identification_link': principals_identification_link,
            'shareholders_link': shareholders_link,
            'declaration_of_trust_link': declaration_of_trust_link,
            'certificate_of_registration_link': certificate_of_registration_link,
            'deed_of_retirement_link': deed_of_retirement_link,
            'business_plan_link': business_plan_link,
            'registered_office_link': registered_office_link,
            'register_of_trustee_link': register_of_trustee_link,
            'proof_of_source_of_funds_link': proof_of_source_of_funds_link,
            'proof_of_source_of_wealth_link': proof_of_source_of_wealth_link,
            'latest_accounts_or_bank_statements_link': latest_accounts_or_bank_statements_link,
            'licence_link': licence_link,
            'certificate_of_incumbency_link': certificate_of_incumbency_link,
            'charter_link': charter_link,
            'latest_accounts_link': latest_accounts_link,
            'principals_foundation_link': identification_documents_of_the_principals_of_the_foundation_link
            })

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

            # print(f"{file_name.capitalize()} Link Before Saving:", file_link)

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

