# views/action_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import ActionSerializer
from ..models import Action, Client
from django.http import Http404
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum

class InitiateActionView(APIView):
    """
    API view for initiating an action associated with a client.
    Requires authentication for access.
    Endpoint: POST /initiate-action/<int:client_id>/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, client_id):
        """Handle POST requests to initiate an action."""
        user = request.user
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            raise Http404("Client does not exist or is not registered")

        title = request.data.get('title')

        # Check for an existing unclosed action with the same title
        existing_action = Action.objects.filter(
            client=client,
            title=title,
            end_time__isnull=True  # Unclosed actions
        ).first()

        if existing_action:
            return Response({'message': 'An unclosed action with the same title already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'user': user.UserID,
            'client': client.id,
            'title': request.data.get('title'),
            'objective': request.data.get('objective'),
        }

        serializer = ActionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Action initiated successfully'})
        else:
            return Response({'message': 'Failed to initiate action', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CloseActionView(APIView):
    """
    API view for closing an active action.
    Requires authentication for access.
    Endpoint: POST /close-action/<int:action_id>/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, action_id):
        """Handle POST requests to close an action."""
        try:
            action = Action.objects.get(id=action_id, is_active=True)
        except Action.DoesNotExist:
            return Response("Action does not exist or is not active.")

        if action.start_time is None:
            return Response({'message': 'Cannot close uninitiated action.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not action.is_active:
            return Response({'message': 'Action already closed'}, status=status.HTTP_400_BAD_REQUEST)

         # Check if the user initiating the action is the same as the user who initiated it   
        if request.user == action.user:
            action.end_time = timezone.now()
            action.description = request.data.get('description', None)

            elapsed_time_seconds = (action.end_time - action.start_time).total_seconds()
            elapsed_time_minutes = Decimal(elapsed_time_seconds) / Decimal(60)  # Convert seconds to minutes

            action.total_elapsed_time += elapsed_time_minutes
            action.is_active = False
            action.save()

            serializer = ActionSerializer(action)
            return Response({'message': 'Action closed successfully', 'action': serializer.data})
        else:
            return Response({'message': 'You do not have permission to close this action'}, status=status.HTTP_403_FORBIDDEN)

class ActionListView(APIView):
    """
    API view for listing actions associated with the authenticated user.
    Requires authentication for access.
    Endpoint: GET /list-actions/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Handle GET requests to list actions."""
        user = request.user
        client_id = self.request.query_params.get('client')
        title = self.request.query_params.get('title')
        is_active = self.request.query_params.get('is_active')
        user_id = self.request.query_params.get('user')

        queryset = Action.objects.filter(user=user)

        # Filter by client ID
        if client_id:
            queryset = queryset.filter(client_id=client_id)

        # Filter by title
        if title:
            queryset = queryset.filter(title=title)

        # Filter by is_active
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # filter by user
        if user_id:
            queryset = Action.objects.filter(user_id=user_id)

        # Calculate total elapsed time
        queryset = queryset.annotate(sum_elapsed_time=Sum('total_elapsed_time'))

        # Sort by default from newest to oldest
        queryset = queryset.order_by('-start_time')

        # Serialize the queryset
        serializer = ActionSerializer(queryset, many=True)
        serialized_data = serializer.data

        return Response(serialized_data, status=status.HTTP_200_OK)
