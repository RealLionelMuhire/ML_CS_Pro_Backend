from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse

class HelloWorldView(APIView):
    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            print("Registration is testUser1*succesfull, now login")

            # Redirect to the login page after successful registration
            login_url = reverse('login')  # Assuming 'login' is the name of your login URL
            return redirect(login_url)
        else:
            print("serialization errors are:")
            print(serializer.errors)
            return Response({'message': 'Registration failed', 'errors': serializer.errors}, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Print or log the entire request.data
        print(f"Request Data: {request.data}")

        # Extract username (email) and password from the request data
        email = request.data.get('email').strip()
        password = request.data.get('password').strip()
        print(f"the user email: {email} and password: {password}")

        # Perform authentication using the email
        user = authenticate(request, email=email, password=password)
        print(f"after authentication the user is : {user}")

        if user is not None:
            # Log in the user
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'message': 'Login failed'}, status=400)

class HelloWorldView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)
