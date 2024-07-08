from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from authentications.views import RegisterView, LoginView
from authentications.serializers import CreateUserSerializer, UserLoginSerializer

from authentications.models import User

class TestRegisterView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_data = {
            'first_name': 'Test User',
            'last_name': 'Test',
            'email': 'test@example.com',
            'password': '強密碼123 (strong_password)',
            'phone': '1234567890'
        }

    def test_register_success(self):
        response = self.client.post('/auth/register/', self.valid_data, format='json')
        self.assertEqual(response.status_code, 201) 
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Registration successful')

        user = get_user_model().objects.get(email=self.valid_data['email'])
        self.assertEqual(user.first_name, self.valid_data['first_name'])
        self.assertEqual(user.last_name, self.valid_data['last_name'])
        self.assertTrue(user.check_password(self.valid_data['password']))

        organisation = Organisation.objects.get(name=f"{user.first_name}'s Organisation")
        self.assertEqual(organisation.users.count(), 1)
        self.assertEqual(organisation.users.first(), user)

    def test_register_invalid_data(self):
        data = self.valid_data.copy()
        del data['password']
        response = self.client.post('/auth/register/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'Bad request')
        self.assertIn('password', response.data['errors'])

        data = self.valid_data.copy()
        data['email'] = 'invalid_email'
        response = self.client.post('/auth/register/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data['errors'])

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
        data = {'email': self.user.email, 'password': 'wrong_password'}
        response = self.client.post('/auth/login/', data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'Bad request')
        self.assertEqual(response.data['message'], 'Authentication failed')
