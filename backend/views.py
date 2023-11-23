from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer

class HelloWorldView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

class RegistrationView(APIView):
    def post(self, request):
        # Implement your registration logic using the provided data
        # For example, you can use the UserSerializer to create a new user
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registration successful'})
        return Response({'message': 'Registration failed'}, status=400)

class LoginView(APIView):
    def post(self, request):
        # Implement your login logic using the provided data
        # For example, you can use the UserSerializer to authenticate the user
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Perform authentication and generate a token if needed
            # Example: token = generate_token(serializer.validated_data)
            return Response({'message': 'Login successful'})
        return Response({'message': 'Login failed'}, status=400)
