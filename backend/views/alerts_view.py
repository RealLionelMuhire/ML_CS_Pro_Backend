from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import permission_classes
from ..models import Client, Alert
from ..serializers import AlertSerializer
from django.http import Http404
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

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
                schedule_date = serializer.validated_data.get('schedule_date')
                expiration_date = serializer.validated_data.get('expiration_date')

                # Validate schedule_date is before expiration_date
                if schedule_date >= expiration_date:
                    raise ValidationError('Schedule date must be before expiration date.')

                # Validate schedule_date is greater than current date
                current_date = timezone.now()
                if schedule_date <= current_date:
                    raise ValidationError('Schedule date must be later than the current date.')

                # Save the alert to the database
                alert = Alert.objects.create(
                    client_id=client_id,
                    user=user,
                    title=serializer.validated_data.get('title'),
                    description=serializer.validated_data.get('description'),
                    action_taken=serializer.validated_data.get('action_taken', False),
                    schedule_date=schedule_date,
                    expiration_date=expiration_date,
                    setter_name=f"{user.FirstName} {user.LastName}",
                    setter_email=user.email,
                    client_name=f"{client.firstName} {client.lastName}",
                    # Add other fields as needed
                )

                return Response({
                    'success': True,
                    'message': f'Alert created successfully. Due on: {alert.schedule_date}. Expires on: {alert.expiration_date}'
                })
            else:
                return Response({'error': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
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
@permission_classes([IsAuthenticated])
class AlertActionView(APIView):
    """
    API view for taking action on an alert.
    Requires authentication for access.
    Endpoint: POST /alert-action/<int:alert_id>/
    """

    def get_alert_or_404(self, alert_id):
        try:
            return Alert.objects.get(id=alert_id)
        except Alert.DoesNotExist:
            raise Http404("Alert does not exist or is not registered")

    def post(self, request, alert_id):
        """
        Handle POST requests to take action on an alert.
        Returns success or error message.
        """
        user = request.user
        alert = self.get_alert_or_404(alert_id)

        # Check if the alert is active
        if not alert.is_active:
            return Response({'message': 'Alert is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Take action on the alert
            alert.action_taken = True
            alert.action_taker_name = f"{user.FirstName} {user.LastName}"
            alert.action_taker_email = user.email
            alert.action_taken_date = timezone.now()
            alert.is_active = False
            alert.save()

            return Response({
                'success': True,
                'message': f'Action taken on the alert. Alert is no longer active.'
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
