# backend/signals.py
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils import timezone
from .models import Alert, UserActionLog

@receiver(post_save, sender=Alert)
def handle_alert_expiration(sender, instance, **kwargs):
    """
    Signal handler to perform actions when an Alert is saved.
    """
    if instance.expiration_date and instance.expiration_date <= timezone.now() and not instance.action_taken:
        # Disconnect the post_save signal temporarily
        post_save.disconnect(handle_alert_expiration, sender=Alert)

        # If expiration_date is passed and action_taken is False
        instance.action_taken_description = "No Action taken"
        instance.is_active = False  # Set is_active to False
        instance.save()

        # Reconnect the post_save signal
        post_save.connect(handle_alert_expiration, sender=Alert)
    elif instance.action_taken:
        # Disconnect the post_save signal temporarily
        post_save.disconnect(handle_alert_expiration, sender=Alert)

        # If action_taken is True
        instance.action_taken_description = f"Action taken by {instance.action_taker_name} on {instance.action_taken_date}"
        instance.is_active = False  # Set is_active to False
        instance.save()

        # Reconnect the post_save signal
        post_save.connect(handle_alert_expiration, sender=Alert)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    # Log user login
    UserActionLog.objects.create(
        user=user,
        action_time=timezone.now(),
        action_type='Login',
    )

@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    # Log user logout
    UserActionLog.objects.create(
        user=user,
        action_time=timezone.now(),
        action_type='Logout',
    )

@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, request, **kwargs):
    # Log failed login attempt
    UserActionLog.objects.create(
        user=None,
        action_time=timezone.now(),
        action_type='Failed Login',
    )
