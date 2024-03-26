# main client views/authentication_views.py

from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseBadRequest
from django.middleware.csrf import get_token
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.utils import timezone
from django.views import View
from datetime import timedelta
from ..models import PasswordResetToken, Service, CustomUser
from rest_framework import status
from django.contrib.auth.hashers import make_password
from ..serializers import UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from decimal import Decimal
from decouple import AutoConfig
from user_permissions import IsClient

config = AutoConfig()

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def client_login_view(request):
    """Handle user login."""
    # Extract username (email) and password from the request data
    # print("testing login")
    email = request.data.get('email').strip()
    password = request.data.get('password').strip()
    # print(f"This is in login_view, Email from frontend before calling authenticate is : {email}, Password: {password}")

    # Perform authentication using the email
    # user = authenticate(request, email=email, password=password)
    user = authenticate(request, username=email, password=password)

    # print(f"This is in login_view, User from backend after email after calling authenticate is: {user}")
    if user is not None:
        # Log in the user
        login(request, user)

        # Generate a new token with a 45-minute expiration time
        token, created = Token.objects.get_or_create(user=user)
        token.created = timezone.now()
        token.save()

        # Serialize the user data
        serializer = UserSerializer(user)
        user_data = serializer.data

        return Response({'message': 'Login successful', 'user_id': user_data['UserID'], 'token': token.key, 'first_name': user_data['FirstName'], 'last_name': user_data['LastName']}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Login failed'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsClient])
def client_logout_view(request):
    """Handle user logout."""
    # Log out the user and invalidate the token
    user = request.user

    # Close all active actions initiated by the user
    active_services = Service.objects.filter(provider_id=user.UserID, is_active=True)
    for service in active_services:
        print("Closing service done: ", service.title)
        service.is_active = False
        service.end_time = timezone.now()
        service.description = "Auto Close By Log Out"
        elapsed_time_seconds = (service.end_time - service.start_time).total_seconds()
        elapsed_time_hours = Decimal(elapsed_time_seconds) / Decimal(3600)

        service.total_elapsed_time = elapsed_time_hours
        service.total_cost = service.service_cost_per_hour * elapsed_time_hours
        
        service.save()
    logout(request)
    request.auth.delete()

    return Response({'message': 'Logout successful'})

def send_password_reset_email(user_email, reset_link):
    subject = 'Password Reset'
    message = f'Click the following link to reset your password: {reset_link}'
    from_email = 'muhirelionel@gmail.com'  # replace with your email
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

class client_ForgotPasswordView(APIView):
    """
    API view for initiating the password reset process.
    Requires AllowAny permission.
    Endpoint: POST /forgot-password/
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Handle POST requests for password reset."""
        # print('==> Start Trying Forgot PWD ==>')
        # Get user email from request.data
        email = request.data.get('email')

        try:
            # Find the user with the provided email
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'message': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Generate token for the user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # print('==> User Found ==>')

        # Construct the reset link
        reset_link = reverse('reset-password', kwargs={'uidb64': uid, 'token': token})

        # For localhost testing, prepend the link
        reset_link = config('EMAIL_LINK') + reset_link

        # Save the token to the database
        token_obj = PasswordResetToken.objects.create(user=user, token=token, expiration_time=timezone.now() + timedelta(days=1))

        # Send the email with the reset link
        send_password_reset_email(email, reset_link)

        return Response({'message': 'Password reset email sent'})


User = get_user_model()
class ResetPasswordView(APIView):
    """
    API view for handling password reset.
    Requires AllowAny permission.
    Endpoint: GET /reset-password/<uidb64>/<token>/
             POST /reset-password/<uidb64>/<token>/
    """
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Render a password reset form."""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Check if the user and token are valid
        if user is not None and default_token_generator.check_token(user, token):
            # Render a password reset form
            print(f"Rendering password reset form for user: {user}")
            return render(request, 'password_reset_form.html', {'uidb64': uidb64, 'token': token})
        else:
            # Token is not valid
            print(f"Invalid token or user not found. User: {user}, Token: {token}")
            return HttpResponseBadRequest('Invalid token or user not found.')

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Handle POST requests for password reset."""
        print(f"Received POST request for password reset with token: {token}")

        # Additional print statements for debugging
        print(f"Received uidb64: {uidb64}")
        
        # Your existing code to handle password reset
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            print(f"User found: {user.email}")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            print(f"Error finding user: {e}")
            return HttpResponseBadRequest('Invalid token or user not found.')

        # Print values for debugging
        print(f"Token: {token}")
        print(f"User: {user}")

        # Check if the token exists in the database
        if PasswordResetToken.objects.filter(token=token, user=user, expiration_time__gt=timezone.now()).exists():
            print(f"Token data found for user: {user.email}")

            # Retrieve the token data
            token_data = PasswordResetToken.objects.get(token=token, user=user, expiration_time__gt=timezone.now())
            
            new_password = request.data.get('new_password')
            user.password = make_password(new_password)
            user.save()

            print(f"Password reset successful for user: {user.email}")

            # Delete the used token
            token_data.delete()

            return Response({'message': 'Password reset successful'})
        else:
            print(f"Token data not found for user: {user.email}")
            return HttpResponseBadRequest('Invalid token or user not found.')
