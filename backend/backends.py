# backend/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            logger.error(f"User with email {username} does not exist.")
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            logger.info(f"User {user} authenticated successfully.")
            return user
        else:
            logger.warning(f"Authentication failed for user {user}.")

        return None
