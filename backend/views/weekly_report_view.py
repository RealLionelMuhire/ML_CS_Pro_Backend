from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics
from django.db import IntegrityError
from django.db import transaction
from django.http import JsonResponse
import base64
import logging
from ..serializers import WeeklyReportSerializer, WeeklyReportUpdateSerializer
from ..models import WeeklyReport
import json


class WeeklyReportRegisterView(APIView):
    """
    Create a new Weekly Report.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = WeeklyReportSerializer(data=request.data)
        user = request.user
        request_data = request.data.copy()
        request_data['user'] = user.UserID

        try:
            request_data.update({
                'reporter_name': user.FirstName + ' ' + user.LastName,
                'reporter_email': user.Email,
                'reporter_id': user.UserID,
            })

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({'error': 'You have already submitted a report for this week.'}, status=status.HTTP_400_BAD_REQUEST)

class WeeklyReportDetailView(APIView):
    """
    API view for retrieving a Weekly Report  by ID.
    Requires authentication.
    Endpoint: /api/weekly_report-detail/{id}/
    """

    serializer_class = WeeklyReportSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get the object by ID
        report_id = self.kwargs['id']
        return get_object_or_404(WeeklyReport, id=report_id)
    
    def retrieve(self, request, *args, **kwargs):
        """Handle GET requests to the endpoint."""
        report = self.get_object()
        serializer = WeeklyReportSerializer(report)
        return Response(serializer.data)

class WeeklyReportUpdateView(APIView):
    """
    API view for updating a Weekly Report by ID.
    Requires authentication.
    Endpoint: /api/weekly_report-update/{id}/
    """

    queryset = WeeklyReport.objects.all()
    serializer_class = WeeklyReportUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def merge_report_table(self, existing_data, incoming_data):
        """
        Merge the existing data with the incoming data.
        """
        existing_dict = {item['id']: item for item in existing_data}
        incoming_dict = {item['id']: item for item in incoming_data}

        for key, value in incoming_dict.items():
            incoming_item = incoming_dict.get(key, {})
            for field in ["id", "taskName", "taskDescription", "progress", "challenges","dateTime",]:
                if incoming_item.get(field) not in [None, ""]:
                    existing_dict[key][field] = incoming_item[field]
        
        merged_data = list(existing_dict.values())
        return merged_data
    
    def perform_update(self, serializer):
        """
        Perform the update operation.
        """

        request = self.request
        request_data = request.data.copy()
        instance = serializer.instance

        # Merge the existing report table with the incoming report table
        existing_data = instance.report_table or []
        incoming_data = request_data.get("report_table", [])
        if isinstance(incoming_data, str):
            incoming_data = json.loads(incoming_data)
        merged_data = self.merge_report_table(existing_data, incoming_data)
        request_data["report_table"] = merged_data

        # Update the serializer with the merged data
        for key, value in request_data.items():
            if key == "report_table":
                setattr(instance, key, merged_data)
            elif value not in ["", None]:
                setattr(instance, key, value)
        instance.save()

    def update(self, request, *args, **kwargs):
        """
        Handle PUT requests to the endpoint.
        """

        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                self.perform_update(serializer)
                return Response(serializer.data)
        except IntegrityError as e:
            return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WeeklyReportDeleteView(APIView):
    """
    API view for deleting a Weekly Report by ID.
    Requires authentication.
    Endpoint: /api/weekly_report-delete/{id}/
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, id, format=None):
        report = get_object_or_404(WeeklyReport, id=id)
        
        try:
            report.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class WeeklyReportListView(APIView):
    """
    API view for retrieving all Weekly Reports.
    Requires authentication.
    Endpoint: /api/weekly_report-list/?ids=1,2,3
    """
    permission_classes = [IsAuthenticated]

    display_fields = {
        "id": "ID",
        "reporter_name": "Reporter Name",
        "reporter_email": "Reporter Email",
        "reporter_id": "Reporter ID",
        "report_table": "Report Table",
        "created_at": "Created At",
        "updated_at": "Updated At",
    }

    def get_queryset(self):
        ids_str = self.request.query_params.get('ids', None)
        ids = [int(id) for id in ids_str.split(",") if id.isdigit()]

        queryset = WeeklyReport.objects.filter(id__in=ids)
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serialized_reports = []

        for id in [int(id) for id in request.query_params.get('ids').split(",")]:
            report = get_object_or_404(queryset, id=id)
            serializer = WeeklyReportSerializer(report)
            serialized_reports.append(serializer.data)

        return Response(serialized_reports)
