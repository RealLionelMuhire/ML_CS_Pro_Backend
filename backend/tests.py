from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APIClient

class RegistrationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user with 'auth.can_create_user' permission
        self.user = get_user_model().objects.create_user(
            email='lionel@gmail.com',
            password='New_Test_Change',
            FirstName='Lionel',
            NationalID='superuser_oTtyXjkzUW',  # Replace with a valid NationalID
            # Add other required fields as needed
        )
        permission = Permission.objects.get(codename='can_create_user')
        self.user.user_permissions.add(permission)

    def test_registration_successful(self):
        url = '/register/'
        data = {
            'email': 'newuser@example.com',
            'FirstName': 'New',
            'LastName': 'User',
            'password': 'newpassword',
            'UserRoles': 'some_role',
            'NationalID': '098760540321',  # Replace with a valid NationalID
            'cv_file': '../../fire_test/cv_file.pdf',  # Replace with the actual file path
            'contract_file': '../../fire_test/contract_file.pdf'  # Replace with the actual file path
        }

        # Authenticate the request with the user having 'auth.can_create_user' permission
        self.client.force_authenticate(user=self.user)

        try:
            response = self.client.post(url, data, format='json')
            print(f"Response status code: {response.status_code}")
            print(f"Response data: {response.data}")
            # Print contract_file and cv_file links for debugging
            print(f"Contract File Link: {response.data.get('contract_file')}")
            print(f"CV File Link: {response.data.get('cv_file')}")
        except Exception as e:
            print(f"Exception during request: {e}")

        self.assertEqual(response.status_code, 200, f"Expected status code 200 but got {response.status_code}")
        # Add more assertions based on your specific requirements
