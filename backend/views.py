# backend/views.py
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import UserSerializer

class HelloWorldView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

class RegistrationView(APIView):
    def post(self, request):
        # Your registration logic here
        return Response({'message': 'Registration successful'})

class LoginView(APIView):
    def post(self, request):
        # Your login logic here
        return Response({'message': 'Login successful'})
