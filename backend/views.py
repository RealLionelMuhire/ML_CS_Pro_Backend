from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db import IntegrityError
from rest_framework import status
from django.http import JsonResponse, Http404
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .serializers import UserSerializer, ActionSerializer, ClientSerializer
from rest_framework.authtoken.views import obtain_auth_token
from datetime import timedelta
from django.utils import timezone
from .models import Client, Action
from rest_framework import generics

class HelloWorldView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    # Extract username (email) and password from the request data
    print("testing login")
    email = request.data.get('email').strip()
    password = request.data.get('password').strip()

    # Perform authentication using the email
    user = authenticate(request, email=email, password=password)
    if user is not None:
        # Log in the user
        login(request, user)

        # Generate a new token with a 45-minute expiration time
        token, created = Token.objects.get_or_create(user=user)
        expiration_time = timezone.now() + timedelta(minutes=1)  # Adjust as needed
        token.created = timezone.now()
        token.save()

        # Serialize the user data
        serializer = UserSerializer(user)
        user_data = serializer.data

        return Response({'message': 'Login successful', 'user_id': user_data['UserID'], 'token': token.key})
    else:
        return Response({'message': 'Login failed'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # Log out the user and invalidate the token
    user = request.user
    logout(request)
    request.auth.delete()

    # Close all active actions initiated by the user
    active_actions = Action.objects.filter(user=user, is_active=True)
    for action in active_actions:
        action.end_time = timezone.now()
        action.is_active = False
        action.save()
        print("Closing actions done")

    return Response({'message': 'Logout successful'})

class ClientRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Retrieve the user from the authenticated request
        user = request.user

        # Combine the user data with the client data
        request_data = request.data
        request_data['user'] = user.UserID  # Replace 'id' with the actual field in your CustomUser model

        # Create the serializer
        serializer = ClientSerializer(data=request_data)

        try:
            if serializer.is_valid():
                # Save the client with the associated user
                client = serializer.save()
                return Response({'message': 'Client registration successful', 'client_id': client.id})
            else:
                return Response({'message': 'Client registration failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return Response({'message': 'Client registration failed. Duplicate client.'}, status=status.HTTP_400_BAD_REQUEST)

class ClientDeleteView(generics.DestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        try:
            client = self.get_object()
            # Check if the authenticated user is the owner of the client
            if request.user != client.user:
                return Response({'message': 'You do not have permission to delete this client.'}, status=status.HTTP_403_FORBIDDEN)
            
            client.delete()
            return Response({'message': 'Client deleted successfully'})
        except Client.DoesNotExist:
            return Response({'message': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_clients(request):
    # Get query parameters from the request
    search_query = request.query_params.get('q', '')

    # Perform the search
    clients = Client.objects.filter(full_name__icontains=search_query)

    # Serialize the results
    serializer = ClientSerializer(clients, many=True)

    return Response(serializer.data)

class ListClientsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clients = Client.objects.all()

        # Serialize the results
        serializer = ClientSerializer(clients, many=True)

        return Response(serializer.data)

class AddFieldToClientView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, client_id):
        # Get the client instance
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({'message': 'Client not found'}, status=404)

        # Check if the user has permission to modify this client
        if request.user != client.user:
            return Response({'message': 'Permission denied'}, status=403)

        # Get the field value from the request data
        field_value = request.data.get('new_field', None)

        # Add the new field to the client
        if field_value is not None:
            client.new_field = field_value
            client.save()
            return Response({'message': 'Field added successfully'})
        else:
            return Response({'message': 'Invalid field value'}, status=400)

class InitiateActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, client_id):
        user = request.user
        try:
            client = Client.objects.get(id=client_id)  # Replace with your actual query
        except Client.DoesNotExist:
            raise Http404("Client does not exist 404 or not registered")

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
            return Response({'message': 'Failed to initiate action', 'errors': serializer.errors}, status=400)

class CloseActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, action_id):
        try:
            action = Action.objects.get(id=action_id, is_active=True)
        except Action.DoesNotExist:
            raise Http404("Action does not exist or is not active.")

        if action.start_time is None:
            return Response({'message': 'Cannot close uninitiated action.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if action.is_active == False:
            return Response({'message': 'action already closed'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user initiating the action is the same as the user who initiated it
        if request.user == action.user:
            action.end_time = timezone.now()
            action.description = request.data.get('description', None)
            action.is_active = False  # Set is_active to False when closing the action
            action.save()

            serializer = ActionSerializer(action)
            return Response({'message': 'Action closed successfully', 'action': serializer.data})
        else:
            return Response({'message': 'You do not have permission to close this action'}, status=403)