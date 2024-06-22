from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import Http404
from django.utils import timezone
from ..helpers.firebase import upload_to_firebase_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..models import Client, Reports
from ..serializers import ReportsSerializer
from django.shortcuts import get_object_or_404
from rest_framework import generics
from django.db import IntegrityError
from django.db import transaction
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

    def handle_file_upload(self, folder, file, file_name):
        logger.info("Handling file upload")
        file_link = None
        msg = None

        if file:
            logger.info(f"File found: {file.name} of size {file.size}")
            file_content = file.read()

            if isinstance(file, InMemoryUploadedFile):
                file_link, msg = upload_to_firebase_storage(folder, file_name, file_content)
            else:
                local_file_path = file.temporary_file_path()
                file_link, msg = upload_to_firebase_storage(folder, file_name, local_file_path)
        else:
            logger.error("No file found")

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
        logger.info(f"Request data: {request_data}")

        client_id = request_data.get('client_id')

        # If client_id is provided, perform client-specific checks
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

        logger.info(f"Updated request data: {request_data}")

        try:
            serializer = ReportsSerializer(data=request_data)
            if serializer.is_valid():
                with transaction.atomic():
                    report = serializer.save()  # Save the report to get the report ID
                logger.info("Report created successfully")

                # Handle file upload after saving the report to get the report ID
                report_file = files_data.get('report_file')
                if report_file:
                    folder = f"report_files/{user.FirstName}_{user.LastName}/{report.id}"
                    report_link, msg = self.handle_file_upload(folder, report_file, 'report.pdf')
                    logger.info(f"Report link: {report_link}, Message: {msg}")
                    if not report_link:
                        return Response({'message': msg}, status=status.HTTP_400_BAD_REQUEST)

                    # Update the report with the file link
                    report.report_link = report_link
                    report.save()
                    logger.info("Report file link updated successfully")

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
    requires authentication for access
    endpoint: GET /reports/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Handle GET requests to list reports."""
        # Retrieve all reports
        reports = Reports.objects.order_by('-created_at')

        # Serialize the reports
        serializer = ReportsSerializer(reports, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class ReportDetailView(generics.ListAPIView):
    """
    API view for retrieving a report by ID.
    requires authentication for access
    endpoint: GET /report-detail/?id=1
    """
    serializer_class = ReportsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the list of report IDs from the query parameters
        report_ids_str = self.request.query_params.get('ids', '')
        report_ids = [int(report_id) for report_id in report_ids_str.split(',') if report_id.isdigit()]

        # Retrieve reports based on the provided IDs
        queryset = Reports.objects.filter(id__in=report_ids)
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Handle GET requests to list reports."""
        queryset = self.get_queryset()
        serialized_reports = []

        # Serialize the reports and handle not found cases
        for report_id in [int(report_id) for report_id in self.request.query_params.get('ids', '').split(',')]:
            report = get_object_or_404(queryset, id=report_id)
            serializer = self.get_serializer(report)
            serialized_reports.append(serializer.data)

        return Response(serialized_reports, status=status.HTTP_200_OK)