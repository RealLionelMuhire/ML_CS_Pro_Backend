# backend/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Alert

@shared_task
def send_reminder_emails():
    """
    Task to send email reminders for alerts that are approaching their schedule date.
    This task will check for alerts that are active, not yet taken action on,
    and scheduled to occur within the next 5 minutes.
    """
    now = timezone.now()
    upcoming_alerts = Alert.objects.filter(
        schedule_date__lte=now + timedelta(minutes=5), 
        is_active=True, 
        action_taken=False
    )

    for alert in upcoming_alerts:
        try:
            send_mail(
                'Reminder Alert',
                f'Your reminder for {alert.title} is approaching!',
                'from@example.com',  # Replace with your "from" email address
                [alert.client_email],
                fail_silently=False,
            )
            alert.action_taken = True
            alert.save()
        except Exception as e:
            # Log the exception if needed
            print(f"Failed to send email for alert {alert.id}: {e}")
