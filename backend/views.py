from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.db import IntegrityError
from rest_framework import status
from django.http import JsonResponse
from .serializers import UserSerializer

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
                return JsonResponse({'message': 'Registration successful', 'user_id': user.id})
            else:
                return Response({'message': 'Registration failed', 'errors': serializer.errors}, status=400)
        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return Response({'message': 'Registration failed. Duplicate user.'}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Extract username (email) and password from the request data
        email = request.data.get('email').strip()
        password = request.data.get('password').strip()

        # Perform authentication using the email
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # Log in the user
            login(request, user)
            return JsonResponse({'message': 'Login successful', 'user_id': user.UserID})  # Use user.UserID
        else:
            return JsonResponse({'message': 'Login failed'}, status=400)