# custom_user_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework import status
from ..serializers import UserSerializer
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes


class HelloWorldView(APIView):
    """
    A simple API view to return a 'Hello, World!' message.
    Requires authentication for access.
    Endpoint: GET /hello-world/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handle GET requests and return a JSON response with a 'Hello, World!' message."""
        content = {'message': 'Hello, World!'}
        return Response(content)


class RegistrationView(APIView):
    """
    API view for user registration, requiring authentication and permission to create a user.
    Endpoint: POST /register/
    Request Payload: Requires 'auth.can_create_user' permission for access.
    Additional information (registered_by_id and registered_by_fullname) is added to the request data.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handle POST requests for user registration."""
        # Check if the user has the permission to create a user
        if not request.user.has_perm('auth.can_create_user'):
            return Response({'message': 'Permission denied. You do not have the required permission to create a user.'}, status=status.HTTP_403_FORBIDDEN)

        # Include additional information in the request data
        request.data['registered_by_id'] = request.user.UserID
        print(f"The user who is registering has an ID {request.user.UserID}")
        request.data['registered_by_fullname'] = request.user.FirstName
        print(f"The user who is registering has the name {request.user.FirstName}")

        # Create a user serializer and handle registration
        serializer = UserSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()
                return JsonResponse({'message': 'Registration successful', 'user_id': user.UserID})
            else:
                return Response({'message': 'Registration failed', 'errors': serializer.errors}, status=400)
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return Response({'message': 'Registration failed. Duplicate user.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_data(request):
    # fetch dashboard data
    data = {'user': request.user.FirstName, 'message': 'Welcome to the dashboard!'}
    return Response(data)