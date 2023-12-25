# views/service_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import ServiceSerializer
from ..models import Service, Client 
from django.http import Http404
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum

class InitiateServiceView(APIView):
    """
    API view for initiating a service associated with a client.
    Requires authentication for access.
    Endpoint: POST /initiate-service/<int:client_id>/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, client_id):
        """Handle POST requests to initiate a service."""
        user = request.user
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            raise Http404("Client does not exist or is not registered")

        # Check if the client is active
        if not client.isActive:
            return Response({'message': f'{client.firstName} {client.lastName} is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        title = request.data.get('title')

        # Check for an existing unclosed service with the same title
        existing_service = Service.objects.filter(
            serviced_client_id=client.id,
            title=title,
            end_time__isnull=True
        ).first()



        if existing_service:
            return Response({'message': 'An unclosed service with the same title already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'user_id': user.UserID,
            'title': request.data.get('title'),
            'objective': request.data.get('objective'),
            'service_cost_per_hour': request.data.get('service_cost_per_hour'),
            'currency': request.data.get('currency'),
            'provider_id': user.UserID,
            'provider_email': user.email,
            'provider_name': f"{user.FirstName} {user.LastName}",
            'is_active': True,
            'client_name': f"{client.firstName} {client.lastName}",
            'client_email': client.clientEmail,
            'serviced_client_id': client.id,
        }
        print(data)

        serializer = ServiceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Service initiated successfully'})
        else:
            return Response({'message': 'Failed to initiate service', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CloseServiceView(APIView):
    """
    API view for closing an active service.
    Requires authentication for access.
    Endpoint: POST /close-service/<int:service_id>/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, service_id):
        """Handle POST requests to close a service."""
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({"message": "Service does not exist or is not active."}, status=status.HTTP_400_BAD_REQUEST)

        if service.start_time is None:
            return Response({'message': 'Cannot close uninitiated service.'}, status=status.HTTP_400_BAD_REQUEST)

        if not service.is_active:
            return Response({'message': 'Service already closed'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user initiating the service is the same as the user who initiated it
        if request.user:
            service.is_active = False
            service.end_time = timezone.now()
            service.description = request.data.get('description', None)

            elapsed_time_seconds = (service.end_time - service.start_time).total_seconds()
            elapsed_time_hours = Decimal(elapsed_time_seconds) / Decimal(3600)

            service.total_elapsed_time = elapsed_time_hours
            service.total_cost = service.service_cost_per_hour * elapsed_time_hours
            
            service.save()

            serializer = ServiceSerializer(service)
            return Response({'message': 'Service closed successfully', 'service': serializer.data})
        else:
            return Response({'message': 'You do not have permission to close this service'}, status=status.HTTP_403_FORBIDDEN)

class ServiceListView(APIView):
    """
    API view for listing services for authenticated user.
    Requires authentication for access.
    Endpoint: GET /list-services/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Handle GET requests to list services."""
        services = Service.objects.all()

        serializer = ServiceSerializer(services, many=True)

        return Response(serializer.data)
