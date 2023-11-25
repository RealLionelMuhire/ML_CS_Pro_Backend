# backend/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        print(f"Checking if user with email {email} exists.")
        UserModel = get_user_model()

        # Print all users in the system
        all_users = UserModel.objects.all()
        print(f"All users: {[user.email for user in all_users]}")

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
