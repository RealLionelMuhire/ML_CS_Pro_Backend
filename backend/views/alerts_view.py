from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from ..models import Client, Alert

@method_decorator(permission_classes([IsAuthenticated]), name='dispatch')
class AlertInitiationView(View):
    """
    API view for initiating an alert for a specific client associated with the authenticated user.
    Requires authentication for access.
    Endpoint: GET /alert-initiate/<int:client_id>/
             POST /alert-initiate/<int:client_id>/
    """

    def get(self, request, client_id):
        """
        Handle GET requests to retrieve the initial data for creating an alert.
        Returns form data and client information.
        """
        try:
            client = Client.objects.get(id=client_id)
            return JsonResponse({'client_data': {'id': client.id, 'name': f"{client.firstName} {client.lastName}", 'email': client.clientEmail}})
        except Client.DoesNotExist:
            return JsonResponse({'error': 'Client not found'}, status=404)

    def post(self, request, client_id):
        """
        Handle POST requests to create an alert.
        Returns success or error message.
        """
        try:
            # Extract data from the JSON request
            data = request.POST.dict()

            # Validate and process the data as needed
            # For example, you might want to ensure required fields are present

            # Save the alert to the database
            alert = Alert.objects.create(
                client_id=client_id,
                user=request.user,
                title=data.get('title'),
                description=data.get('description'),
                action_taken=data.get('action_taken', False),
                schedule_date=data.get('schedule_date'),
                expiration_date=data.get('expiration_date')
                # Add other fields as needed
            )

            return JsonResponse({'success': True, 'message': 'Alert created successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
