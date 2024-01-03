from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import permission_classes
from ..models import Client, Alert
from ..serializers import AlertSerializer
from django.http import Http404

@permission_classes([IsAuthenticated])
class AlertInitiationView(APIView):
    """
    API view for initiating an alert for a specific client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: POST /alert-initiate/<int:client_id>/
    """

    def get_client_or_404(self, client_id):
        try:
            return Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            raise Http404("Client does not exist or is not registered")

    def post(self, request, client_id):
        """
        Handle POST requests to create an alert.
        Returns success or error message.
        """
        user = request.user
        client = self.get_client_or_404(client_id)

        # Check if the client is active
        if not client.isActive:
            return Response({'message': f'{client.firstName} {client.lastName} is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate and process the data using a serializer
            serializer = AlertSerializer(data=request.data)
            if serializer.is_valid():
                # Save the alert to the database
                alert = Alert.objects.create(
                    client_id=client_id,
                    user=user,
                    title=request.data.get('title'),
                    description=request.data.get('description'),
                    action_taken=request.data.get('action_taken', False),
                    schedule_date=request.data.get('schedule_date'),
                    expiration_date=request.data.get('expiration_date'),
                    setter_name=f"{user.FirstName} {user.LastName}",
                    setter_email=user.email,
                    client_name=f"{client.firstName} {client.lastName}",
                    # Add other fields as needed
                )

                return Response({'success': True, 'message': 'Alert created successfully'})
            else:
                return Response({'error': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AlertListView(APIView):
    """
    API view for listing all alerts associated with the authenticated user.
    Requires authentication for access.
    Endpoint: GET /list-alerts/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Handle GET requests to list alerts."""
        # Retrieve all alerts associated with the authenticated user
        alerts = Alert.objects.filter(user=request.user)

        # Serialize the alerts
        serializer = AlertSerializer(alerts, many=True)

        return Response(serializer.data)

