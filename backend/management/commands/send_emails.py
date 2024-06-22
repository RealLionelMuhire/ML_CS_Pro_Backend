# backend/management/commands/send_emails.py
from django.core.management.base import BaseCommand
from backend.tasks import send_reminder_emails

class Command(BaseCommand):
    help = 'Manually trigger send_reminder_emails task'

    def handle(self, *args, **kwargs):
        send_reminder_emails.apply_async()
        self.stdout.write(self.style.SUCCESS('Successfully triggered send_reminder_emails task'))

