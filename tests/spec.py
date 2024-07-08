from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from authentications.views import RegisterView, LoginView
from authentications.serializers import CreateUserSerializer, UserLoginSerializer
from authentications.models import User, Organisation

class TestRegisterView(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success_with_default_organisation(self):
        valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'strong_password',
            'phone': '1234567890'
        }

        response = self.client.post('/auth/register/', valid_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Registration successful')

        user = get_user_model().objects.get(email=valid_data['email'])
        self.assertEqual(user.first_name, valid_data['first_name'])
        self.assertEqual(user.last_name, valid_data['last_name'])

        # Check default organisation creation
        organisation = Organisation.objects.get(name=f"{user.first_name}'s Organisation")
        self.assertEqual(organisation.users.count(), 1)
        self.assertEqual(organisation.users.first(), user)

        # Check response data
        self.assertIn('accessToken', response.data['data'])
        user_data = response.data['data']['user']
        self.assertEqual(user_data['userId'], user.userId)
        self.assertEqual(user_data['firstName'], user.first_name)
        self.assertEqual(user_data['lastName'], user.last_name)
        self.assertEqual(user_data['email'], user.email)
        self.assertEqual(user_data['phone'], user.phone)

        # Check access token validity
        self.assertIn('accessToken', response.data['data'])
        access_token = response.data['data']['accessToken']


    def test_register_failure_with_invalid_data(self):
        invalid_data = {
            'email': 'john.doe@example.com',  # Missing some required fields
        }

        response = self.client.post('/auth/register/', invalid_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'Bad request')
        self.assertEqual(response.data['message'], 'Registration unsuccessful')
        self.assertIn('errors', response.data)


class TestLoginView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='strong_password',
            first_name='Test',
            last_name='User',
        )

    def test_login_success(self):
        data = {'email': self.user.email, 'password': 'strong_password'}
        response = self.client.post('/auth/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Login successful')
        self.assertIn('accessToken', response.data['data'])

    def test_login_invalid_credentials(self):
        data = {'email': self.user.email, 'password': 'invalid_password'}
        response = self.client.post('/auth/login/', data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'Bad request')
        self.assertEqual(response.data['message'], 'Authentication failed')