from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import Http404
from django.utils import timezone
from ..helpers.firebase import upload_to_firebase_storage, download_file_from_url
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..models import Client, Reports
from ..serializers import ReportsSerializer, ReportUpdateSerializer
from django.shortcuts import get_object_or_404
from rest_framework import generics
from django.db import IntegrityError
from django.db import transaction
import base64
import logging

logger = logging.getLogger(__name__)

class ReportsCreateView(APIView):
    """
    API view for Creating a report
    Requires authentication for access.
    Endpoint: POST /api/create-report/
    """
    permission_classes = [IsAuthenticated]

    def get_client_or_404(self, client_id):
        try:
            return Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            raise Http404("Client does not exist or is not registered")

    def handle_file_upload(self, reporter_name, request, file_key, report_id):
        logger.info("Handling file upload")
        file = request.FILES.get(file_key)
        file_link = None
        msg = None

        if file:
            logger.info(f"File found: {file.name} of size {file.size}")
            # Use reporter_name from serializer
            folder = f"reports_files/{reporter_name}"
            file_name = f"report_{report_id}.pdf"
            file_content = file.read()

            if isinstance(file, InMemoryUploadedFile):
                file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link, msg = upload_to_firebase_storage(folder, file_name, local_file_path)
        else:
            logger.error(f"No file found for key: {file_key}")

        return file_link, msg

    def post(self, request):
        logger.info("Entered ReportsCreateView POST method")
        """
        Handle POST requests to create a report.
        Returns success or error message.
        """
        user = request.user
        request_data = {key: value for key, value in request.data.items()}  # Create a shallow copy of the request data
        files_data = request.FILES  # Use files directly from the request
        # logger.info(f"Request data: {request_data}")

        client_id = request_data.get('client_id')

        # If client_id is provided, perform client-specific checks
        if client_id:
            client = self.get_client_or_404(client_id)
            # logger.info(f"Client: {client}")
            # Check if the client is active
            if not client.isActive:
                return Response({'message': f'{client.firstName} {client.lastName} is not active.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update request data with client-specific information
            request_data['client_reportee_id'] = client_id
            request_data['client_reportee_name'] = f"{client.firstName} {client.lastName}"
            request_data['client_reportee_email'] = client.clientEmail
        else:
            # If client_id is not provided, ensure these fields are set to None or empty
            request_data['client_reportee_id'] = None
            request_data['client_reportee_name'] = None
            request_data['client_reportee_email'] = None

        # Update request data with common fields
        request_data['created_at'] = timezone.now()
        request_data['updated_at'] = timezone.now()
        request_data['reporter_id'] = user.UserID
        request_data['reporter_email'] = user.email
        request_data['reporter_name'] = f"{user.FirstName} {user.LastName}"

        # logger.info(f"Updated request data: {request_data}")

        try:
            serializer = ReportsSerializer(data=request_data)
            if serializer.is_valid():
                with transaction.atomic():
                    report = serializer.save()  # Save the report to get the report ID
                # logger.info("Report created successfully")

                # Handle file upload after saving the report to get the report ID
                report_file = files_data.get('report_file')
                reporter_name = request_data['reporter_name']
                if report_file:
                    report_link, msg = self.handle_file_upload(reporter_name, request, 'report_file', report.id)
                    # logger.info(f"Report link: {report_link}, Message: {msg}")
                    if not report_link:
                        return Response({'message': msg}, status=status.HTTP_400_BAD_REQUEST)

                    # Update the report with the file link
                    report.report_link = report_link
                    report.save()
                    # logger.info("Report file link updated successfully")

                return Response({'message': 'Report created successfully'}, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            return Response({'message': str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            logger.error(f"Error during the report creation process: {str(e)}")
            return Response({'message': 'An error occurred during the report creation process.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ReportListView(APIView):
    """
    API view for listing reports
    Requires authentication for access
    Endpoint: GET /reports/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Handle GET requests to list reports."""
        # Retrieve all reports
        reports = Reports.objects.order_by('-created_at')

        # Serialize the reports
        serializer = ReportsSerializer(reports, many=True)
        response_data = serializer.data

        # Iterate through each report and handle file downloads
        for report in response_data:
            report_id = report.get('id')
            report_link = report.get('report_link')

            if report_link:
                try:
                    file_name, file_content = download_file_from_url(report_link)
                    if file_content:
                        report['report_file'] = {
                            'file_name': file_name,
                            'file_content': base64.b64encode(file_content.getvalue()).decode('utf-8')
                        }
                except Exception as e:
                    logger.error(f"Failed to download file for report {report_id}: {str(e)}")
                    report['report_file'] = None  # Or handle this as needed

        return Response(response_data, status=status.HTTP_200_OK)

class ReportUpdateView(APIView):
    """
    API view for updating a report.
    Requires authentication for access.
    Endpoint: PUT /api/update-report/<int:report_id>/
    """
    permission_classes = [IsAuthenticated]

    def handle_file_upload(self, reporter_name, request, file_key, report_id):
        logger.info("Handling file upload")
        file = request.FILES.get(file_key)
        file_link = None
        msg = None

        if file:
            logger.info(f"File found: {file.name} of size {file.size}")
            folder = f"reports_files/{reporter_name}"
            file_name = f"report_{report_id}.pdf"
            file_content = file.read()

            if isinstance(file, InMemoryUploadedFile):
                file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link, msg = upload_to_firebase_storage(folder, file_name, local_file_path)
        else:
            logger.error(f"No file found for key: {file_key}")

        return file_link, msg

    def get_client_or_404(self, client_id):
        return get_object_or_404(Client, id=client_id)

    def put(self, request, report_id):
        logger.info("Entered ReportUpdateView PUT method")
        logger.info(f"Request data: {request.data}")

        report = get_object_or_404(Reports, id=report_id)
        logger.info(f"Original report data: {report.__dict__}")

        # Create a mutable copy of request.data
        request_data = request.data.copy()

        # Extract the client_reportee_id from request data if it exists
        client_id = request_data.get('client_id')

        if client_id:
            client = self.get_client_or_404(client_id)
            logger.info(f"Client: {client}")

            # Check if the client is active
            if not client.isActive:
                return Response({'message': f'{client.firstName} {client.lastName} is not active.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update request data with client-specific information
            request_data['client_reportee_id'] = client_id
            request_data['client_reportee_name'] = f"{client.firstName} {client.lastName}"
            request_data['client_reportee_email'] = client.clientEmail

        serializer = ReportUpdateSerializer(report, data=request_data, partial=True)
        if serializer.is_valid():
            logger.info(f"Validated data: {serializer.validated_data}")
            try:
                with transaction.atomic():
                    updated_fields = {}

                    for field, value in serializer.validated_data.items():
                        if value is not None and value != '':
                            setattr(report, field, value)
                            updated_fields[field] = value

                    # Handle file upload if a new file is provided
                    report_file = request.FILES.get('report_file')
                    reporter_name = f"{request.user.FirstName} {request.user.LastName}"
                    if report_file:
                        report_link, msg = self.handle_file_upload(reporter_name, request, 'report_file', report_id)
                        logger.info(f"Report link: {report_link}, Message: {msg}")
                        if not report_link:
                            return Response({'message': msg}, status=status.HTTP_400_BAD_REQUEST)
                        report.report_link = report_link
                        updated_fields['report_link'] = report_link

                    # Save the updated report
                    report.last_updated_by_id = request.user.UserID
                    report.last_updated_by_name = f"{request.user.FirstName} {request.user.LastName}"
                    report.save()

                    logger.info(f"Updated report data: {report.__dict__}")
                    logger.info(f"Report updated successfully with fields: {updated_fields}")
                    return Response({'message': 'Report updated successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error during the report update process: {str(e)}")
                return Response({'message': 'An error occurred during the report update process.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ReportDetailView(generics.RetrieveAPIView):
    """
    API view for retrieving a report by ID.
    Requires authentication for access.
    Endpoint: GET /report-detail/{id}/
    """
    serializer_class = ReportsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get the report ID from the URL
        report_id = self.kwargs.get('id')
        logger.info(f"Fetching report with ID: {report_id}")

        # Retrieve the report based on the provided ID
        report = get_object_or_404(Reports, id=report_id)
        return report

    def retrieve(self, request, *args, **kwargs):
        """Handle GET requests to retrieve a report."""
        report = self.get_object()
        serializer = self.get_serializer(report)
        report_data = serializer.data

        # Download report file if report_link is available
        report_link = report_data.get('report_link')
        if report_link:
            try:
                file_name, file_content = download_file_from_url(report_link)
                if file_content:
                    report_data['report_file'] = {
                        'file_name': file_name,
                        'file_content': base64.b64encode(file_content.getvalue()).decode('utf-8')
                    }
            except Exception as e:
                logger.error(f"Failed to download file for report {report.id}: {str(e)}")
                report_data['report_file'] = None  # Or handle this as needed

        # logger.info(f"Report data: {report_data}")
        return Response(report_data, status=status.HTTP_200_OK)
class ReportDeleteView(APIView):
    """
    API view for deleting a report by ID.
    Requires authentication for access.
    Endpoint: DELETE /report-delete/<id>/
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, report_id):
        """
        Handle DELETE requests to delete a report.
        """
        report = get_object_or_404(Reports, id=report_id)

        try:
            report.delete()
            return Response({'message': 'Report deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting report: {str(e)}")
            return Response({'message': 'An error occurred during the report deletion process.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReportListByIdView(generics.ListAPIView):
    """
    API view for retrieving a list of reports by IDs.
    Requires authentication for access.
    Endpoint: GET /report-list-by-id/?ids=1,2,3
    """

    permission_classes = [IsAuthenticated]

    display_fields_map = {
        'id': 'id',
        'client_reportee_id': 'client reportee id',
        'client_reportee_name': 'client reportee name',
        'client_reportee_email': 'client reportee email',
        'reporter_id': 'reporter id',
        'reporter_email': 'reporter email',
        'reporter_name': 'reporter name',
        'created_at': 'reported at',
        'updated_at': 'modified at',
        'last_updated_by_name': 'last updated by name',
        'last_updated_by_id': 'last updated by id',
        'last_updated_by_email': 'last updated by email',
        'title': 'title',
        'description': 'description',
        'report_link': 'report link',

    }

    def get_queryset(self):
        # Get the list of report IDs from the query parameters
        report_ids_str = self.request.query_params.get('ids', '')
        report_ids = [int(report_id) for report_id in report_ids_str.split(',') if report_id.isdigit()]

        # Filter and retrieve reports based on the provided IDs
        queryset = Reports.objects.filter(id__in=report_ids)
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serialized_reports = []

        # Serialize the reports and handle not found cases
        for report_id in [int(report_id) for report_id in self.request.query_params.get('ids', '').split(',')]:
            report = get_object_or_404(queryset, id=report_id)
            serializer = ReportsSerializer(report)
            report_data = serializer.data

            # Handle file download and base64 encoding
            report_link = report_data.get('report_link')
            if report_link:
                try:
                    file_name, file_content = download_file_from_url(report_link)
                    if file_content:
                        report_data['report_file'] = {
                            'file_name': file_name,
                            'file_content': base64.b64encode(file_content.getvalue()).decode('utf-8')
                        }
                except Exception as e:
                    report_data['report_file'] = {
                        'error': f"Failed to download file: {str(e)}"
                    }

            # Map the fields to user-friendly names and include only those in display_fields_map
            mapped_data = {self.display_fields_map[k]: report_data[k] for k in self.display_fields_map if k in report_data}

            # Include the file data in the mapped data
            if 'report_file' in report_data:
                mapped_data['report file'] = report_data['report_file']

            serialized_reports.append(mapped_data)

        return Response(serialized_reports)