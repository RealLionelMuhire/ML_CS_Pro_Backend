# backend/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        user = UserModel.objects.filter(Q(email__iexact=username) | Q(username__iexact=username)).first()
        messages = []

        if not user:
            messages.append("User not found.")

        elif not user.check_password(password):
            messages.append("Incorrect password.")

        if messages:
            return (None, messages)

        return user, []
