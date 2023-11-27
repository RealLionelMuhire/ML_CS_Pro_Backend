from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.db import IntegrityError
from rest_framework import status
from django.http import JsonResponse
from rest_framework.authtoken.models import Token  # Add this line
from .serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    # Extract username (email) and password from the request data
    email = request.data.get('email').strip()
    password = request.data.get('password').strip()

    # Perform authentication using the email
    user = authenticate(request, email=email, password=password)
    if user is not None:
        # Log in the user
        login(request, user)

        # Generate a new token
        token, created = Token.objects.get_or_create(user=user)

        return Response({'message': 'Login successful', 'user_id': user.UserID, 'token': token.key})
    else:
        return Response({'message': 'Login failed'}, status=400)