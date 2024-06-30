# backend/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Alert
from decouple import AutoConfig
import logging

config = AutoConfig()
logger = logging.getLogger(__name__)

@shared_task
def send_reminder_emails():
    """
    Task to send email reminders for alerts that are approaching their schedule date.
    This task will check for alerts that are active, not yet taken action on,
    and scheduled to occur within the next 5 minutes.
    """
    now = timezone.now()
    two_days = timedelta(days=2)
    one_day = timedelta(days=1)

    upcoming_alerts = Alert.objects.filter(
        schedule_date__gte=now - two_days,
        is_active=True,
        action_taken=False,
        reminder_email_count__lt=3
    )

    # Log the number of upcoming alerts
    logger.info(f"Number of upcoming alerts: {upcoming_alerts.count()}")

    for alert in upcoming_alerts:
        send_email = False
        if alert.reminder_email_count == 0 and now >= alert.schedule_date - two_days:
            send_email = True
        elif alert.reminder_email_count == 1 and now >= alert.schedule_date - one_day:
            send_email = True
        elif alert.reminder_email_count == 2 and now >= alert.schedule_date:
            send_email = True

        if send_email:
            try:
                email_subject = f'Reminder of {alert.title}'
                email_body = (
                    f'Dear {alert.setter_name},\n\n'
                    f'This is a reminder for the task "{alert.title}".\n\n'
                    f'Description: {alert.description}\n'
                    f'Scheduled Date: {alert.schedule_date}\n'
                    f'Expiration Date: {alert.expiration_date}\n\n'
                    f'Please take the necessary actions before the expiration date.\n\n'
                    f'Thank you,\n'
                    f'ML Corporate Services Reminder System'
                )

                send_mail(
                    email_subject,
                    email_body,
                    config("EMAIL_HOST_USER"),
                    [alert.setter_email],
                    fail_silently=False,
                )
                
                alert.reminder_email_count += 1
                alert.last_reminder_sent = now
                # if alert.reminder_email_count >= 3:
                #     alert.is_active = False

                alert.save()
                logger.info(f"Successfully sent email for alert {alert.id} to {alert.setter_email}")
            except Exception as e:
                logger.error(f"Failed to send email for alert {alert.id}: {e}")
