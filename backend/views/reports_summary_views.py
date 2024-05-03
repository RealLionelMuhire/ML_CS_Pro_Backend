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
