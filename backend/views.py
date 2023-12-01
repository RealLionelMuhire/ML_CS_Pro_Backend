from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db import IntegrityError
from rest_framework import status
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .serializers import UserSerializer
from rest_framework.authtoken.views import obtain_auth_token
from datetime import timedelta
from django.utils import timezone
from .serializers import ClientSerializer

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
    logout(request)
    request.auth.delete()

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
