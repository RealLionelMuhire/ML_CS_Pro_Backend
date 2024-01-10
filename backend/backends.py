# backend/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        # print(f"This is backend.py in <authenticatte function> Email from login_view is: {username}, Password: {password}")

        # Check if the provided username or email is a valid email
        user = UserModel.objects.filter(Q(email__iexact=username) | Q(username__iexact=username)).first()

        # print(f"This is backend.py in <authenticatte function> User from backend after email authentication is: {user}")


        if user:
            if user.check_password(password):
                print(f"User {user} authenticated successfully.")
                return user
            else:
                # print(f"Authentication error: Incorrect password. the user email is {user}")
                return None, "Authentication error: Incorrect password."
        else:
            # print("Authentication error: User not found.")
            return None, "Authentication error: User not found."

        return None
