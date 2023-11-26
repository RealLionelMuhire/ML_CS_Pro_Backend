# backend/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist as e:
            print(f"User with email {email} does not exist. Error: {e}")
            return None

        if user.check_password(password):
            print(f"User {user} authenticated successfully.")
            return user
        
        print("Authentication error: Password does not match.")
        return None
