from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import Http404
from django.utils import timezone
from ..helpers.firebase import upload_to_firebase_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..models import Client, Reports
from ..serializers import ReportsSerializer
from django.shortcuts import get_object_or_404

class ReportsListView(APIView):
    """
    API view for Creating a report
    requires authentication for access
    endpoint: POST /create-report/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle POST requests to create a report.
        Returns success or error message.
        """
        user = request.user
        request_data = request.data
        request_data['user'] = user.UserID
        report_link = self.handle_file_upload(request, 'report_file', 'report.pdf')

        # Check if client_id is present and not empty in the request data
        client_id = request_data.get('client_id')
        if client_id:
            client = self.get_client_or_404(client_id)
            request_data.update({
                'client_reportee_id': client.id,
                'client_reportee_email': client.email,
                'client_reportee_name': client.name
            })

        request.data.update({
            'report_link': report_link,
            'created_at': timezone.now(),
            'updated_at': timezone.now(),
            'reporter_id': user.UserID,
            'reporter_email': user.email,
            'reporter_name': f"{user.FirstName} {user.LastName}",
        }) 

        # Your existing code for handling file upload goes here

    def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None

        if file:
            folder = f"reports_files/{request.data['FirstName']}_{request.data['LastName']}"
            file_content = file.read()
            file_checksum = request.data.get(f'{file_key}_checksum')

            if isinstance(file, InMemoryUploadedFile):
                file_link = upload_to_firebase_storage(folder, file_name, file_content, file_checksum)
            else:
                local_file_path = file.temporary_file_path()
                file_link = upload_to_firebase_storage(folder, file_name, local_file_path, file_checksum)

        return file_link

    def get_client_or_404(self, client_id):
        try:
            return Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            raise Http404("Client does not exist or is not registered")

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