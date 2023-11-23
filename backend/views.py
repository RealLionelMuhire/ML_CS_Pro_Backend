from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated

class HelloWorldView(APIView):
    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

class RegistrationView(APIView):
    permission_classes = [AllowAny]  # Allow any user (authenticated or not) to register

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Registration successful'})
        return Response({'message': 'Registration failed'}, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow any user (authenticated or not) to log in

    def post(self, request):
        # Extract username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')

        # Perform authentication
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log in the user
            login(request, user)
            return Response({'message': 'Login successful'})
        else:
            return Response({'message': 'Login failed'}, status=400)

class HelloWorldView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)
