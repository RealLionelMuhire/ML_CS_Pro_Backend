from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Admission

class AdmissionTest(APITestCase):
    def setUp(self):
        # Create a user who can grant admission
        self.grantor = get_user_model().objects.create_user(
            email='grantor@example.com',
            username='grantor_user',
            password='testpassword',
        )

        # Create a user who wants to register
        self.grantee_data = {
            'email': 'grantee@example.com',
            'full_name': 'Grantee User',
            'role': 'Test Role',
        }

    def test_admission_process(self):
        # Grant admission
        grant_admission_url = reverse('admission')
        admission_data = {
            'grantee_email': self.grantee_data['email'],
            'grantee_full_name': self.grantee_data['full_name'],
        }

        self.client.force_authenticate(user=self.grantor)
        response = self.client.post(grant_admission_url, admission_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Attempt registration with granted admission
        registration_url = reverse('user-registration-request')
        response = self.client.post(registration_url, self.grantee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Attempt registration without admission
        response = self.client.post(registration_url, self.grantee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

