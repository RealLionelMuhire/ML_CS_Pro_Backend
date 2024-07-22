from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.conf import settings
from time import sleep

class SessionExpiryMiddlewareTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token, created = Token.objects.get_or_create(user=self.user)

    def test_session_expiry(self):
        # Log in the user
        login_response = self.client.post('/api/login/', {'email': 'testuser', 'password': 'testpassword'}, content_type='application/json')
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('token', login_response.json())
        
        # Set session expiry to 60 seconds
        self.client.session.set_expiry(60)
        self.client.session.save()

        # Make an authenticated request
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/some_protected_view/')
        self.assertEqual(response.status_code, 200)

        # Sleep for 61 seconds to expire the session
        sleep(61)

        # Make another request which should fail due to expired session
        response = self.client.get('/api/some_protected_view/')
        self.assertEqual(response.status_code, 401)

        # Check if the token is deleted
        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(key=self.token.key)

        # Check if the user is logged out
        response = self.client.get('/api/some_protected_view/')
        self.assertEqual(response.status_code, 401)
