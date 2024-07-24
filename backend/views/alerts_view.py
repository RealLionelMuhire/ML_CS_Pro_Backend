from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from ..models import Client, Alert
from ..serializers import AlertSerializer
from django.http import Http404
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics


class AlertInitiationView(APIView):
    """
    API view for initiating an alert for a specific client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: POST /alert-initiate/
    """
    permission_classes = ([IsAuthenticated])

    def get_client_or_404(self, client_id):
        try:
            return Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            raise Http404("Client does not exist or is not registered")

    def post(self, request):
        """
        Handle POST requests to create an alert.
        Returns success or error message.
        """
        user = request.user
        client_id = request.data.get('client_id')

        # If client_id is provided, perform client-specific checks
        if client_id:
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
                current_date = timezone.now().date()
                if schedule_date <= current_date:
                    raise ValidationError('Schedule date must be later than the current date.')

                # Save the alert to the database
                alert = Alert.objects.create(
                    client_id=client_id if client_id else None,
                    user=user,
                    title=serializer.validated_data.get('title'),
                    description=serializer.validated_data.get('description'),
                    schedule_date=serializer.validated_data.get('schedule_date'),
                    expiration_date=serializer.validated_data.get('expiration_date'),
                    setter_name=f"{user.FirstName} {user.LastName}",
                    setter_email=user.email,
                    client_name=f"{client.firstName} {client.lastName}" if client_id else None,
                    client_email=client.clientEmail if client_id else None,
                    set_date=timezone.now().date(),
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
        # Retrieve all alerts
        alerts = Alert.objects.order_by('schedule_date')

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

class AlertDetailView(generics.ListAPIView):
    """"
    API view for viewing a single alert by its ID.
    Requires authentication for access.
    Endpoint: GET /alert-detail/<int:alert_id>/
    """

    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        # Get the list of alert IDs from the query parameters
        alert_ids_str = self.request.query_params.get('ids', '')
        alert_ids = [int(alert_id) for alert_id in alert_ids_str.split(',') if alert_id.isdigit()]

        # Filter and retrieve alerts based on the provided IDs
        queryset = Alert.objects.filter(id__in=alert_ids)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serialized_alerts = []

        # Serialize the alerts and handle not found cases
        for alert_id in [int(alert_id) for alert_id in self.request.query_params.get('ids', '').split(',')]:
            alert = get_object_or_404(queryset, id=alert_id)
            serializer = self.get_serializer(alert)
            serialized_alerts.append(serializer.data)

        return Response(serialized_alerts)

class ActiveAlertsView(APIView):
    """
    API view for listing active alerts associated with the authenticated user.
    Requires authentication for access.
    Endpoint: GET /active-alerts/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Handle GET requests to list active alerts."""
        # Retrieve active alerts associated with the authenticated user
        active_alerts = Alert.objects.filter( is_active=True).order_by('schedule_date')

        # Serialize the active alerts
        serializer = AlertSerializer(active_alerts, many=True)

        return Response(serializer.data)
