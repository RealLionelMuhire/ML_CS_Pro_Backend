# backend/middlewares.py

import time
from django.contrib.auth import get_user_model, logout
from .models import Request
from django.utils import timezone
from django.contrib.sessions.models import Session
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)

class SaveRequest:
    def __init__(self, get_response):
        self.get_response = get_response

        # URLs that should be logged
        self.prefixes = ['/example']

    def __call__(self, request):
        start_time = time.time()  # Record start time for execution

        # Get the response from the view function
        response = self.get_response(request)

        # Calculate the execution time in milliseconds
        exec_time = int((time.time() - start_time) * 1000)

        # Check if the request URL starts with any of the specified prefixes
        if not any(request.path.startswith(prefix) for prefix in self.prefixes):
            return response  # If not, return the response without saving log

        # Create an instance of the Request model and assign values
        request_log = Request(
            endpoint=request.path,
            response_code=response.status_code,
            method=request.method,
            remote_address=self.get_client_ip(request),
            exec_time=exec_time,
            body_response=str(response.content),
            body_request=str(request.body)
        )

        # Assign user to log if it's not an anonymous user
        if not request.user.is_anonymous:
            request_log.user = request.user

        # Save log in the database
        request_log.save()

        return response

    # Get client's IP address
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        else:
            return request.META.get('REMOTE_ADDR')

class SessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session_key = request.session.session_key
        if session_key:
            try:
                session = Session.objects.get(session_key=session_key)
                expiry_date = session.expire_date
                if expiry_date < timezone.now():
                    # Session has expired
                    user = request.user
                    if user.is_authenticated:
                        # Log out the user and delete the token
                        Token.objects.filter(user=user).delete()
                        logout(request)
            except Session.DoesNotExist:
                pass  # No session found, nothing to do

        response = self.get_response(request)
        return response