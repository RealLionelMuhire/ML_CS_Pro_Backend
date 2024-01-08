# backend/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        # Check if the provided username or email is a valid email
        user = UserModel.objects.filter(Q(email__iexact=username) | Q(username__iexact=username)).first()

        if user and user.check_password(password):
            print(f"User {user} authenticated successfully.")
            return user

        print("Authentication error: User or password does not match.")
        return None
