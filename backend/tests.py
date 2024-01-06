from django.test import TestCase
from django.utils import timezone
from backend.models import Alert
from backend.signals import handle_alert_expiration

class AlertSignalTests(TestCase):
    def test_handle_alert_expiration_no_action_taken(self):
        # Create an Alert with expiration_date in the past and action_taken is False
        alert = Alert.objects.create(
            title='Test Alert',
            description='This is a test alert',
            action_taken=False,
            schedule_date=timezone.now(),
            expiration_date=timezone.now() - timezone.timedelta(days=1),
        )

        # Print test description
        print("Running test_handle_alert_expiration_no_action_taken")

        # Call the signal handler manually
        handle_alert_expiration(sender=Alert, instance=alert)

        # Retrieve the updated alert from the database
        updated_alert = Alert.objects.get(id=alert.id)

        # Ensure action_taken_description is set to "No Action taken"
        self.assertEqual(updated_alert.action_taken_description, "No Action taken")

        # Print additional information
        print(f"Alert ID: {updated_alert.id}")
        print(f"Updated Action Taken Description: {updated_alert.action_taken_description}")

    def test_handle_alert_expiration_with_action_taken(self):
        # Create an Alert with expiration_date in the past and action_taken is True
        alert = Alert.objects.create(
            title='Test Alert',
            description='This is a test alert',
            action_taken=True,
            action_taker_name='Test User',
            action_taken_date=timezone.now(),
            schedule_date=timezone.now(),
            expiration_date=timezone.now() - timezone.timedelta(days=1),
        )

        # Print test description
        print("Running test_handle_alert_expiration_with_action_taken")

        # Call the signal handler manually
        handle_alert_expiration(sender=Alert, instance=alert)

        # Retrieve the updated alert from the database
        updated_alert = Alert.objects.get(id=alert.id)

        # Ensure action_taken_description is set to the expected value
        expected_description = f"Action taken by {alert.action_taker_name} on {alert.action_taken_date}"
        self.assertEqual(updated_alert.action_taken_description, expected_description)

        # Print additional information
        print(f"Alert ID: {updated_alert.id}")
        print(f"Updated Action Taken Description: {updated_alert.action_taken_description}")
