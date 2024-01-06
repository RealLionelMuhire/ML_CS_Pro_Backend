# backend/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Alert

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
