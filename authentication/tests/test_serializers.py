from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..serializers import CustomAuthTokenSerializer, UserSerializer
from datetime import datetime, timezone


User = get_user_model()

class CustomAuthTokenSerializerTest(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )

        # Create an API client for making requests
        self.client = APIClient()

    def test_custom_auth_token_serializer_valid(self):
        # Test the serializer with valid data
        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
        }
        serializer = CustomAuthTokenSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_custom_auth_token_serializer_invalid_email(self):
        # Test the serializer with an invalid email
        data = {
            'email': 'invalid@example.com',
            'password': 'testpassword',
        }
        serializer = CustomAuthTokenSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('No such user found with this email', serializer.errors.get('non_field_errors', []))

    def test_custom_auth_token_serializer_invalid_password(self):
        # Test the serializer with an invalid password
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword',
        }
        serializer = CustomAuthTokenSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Incorrect password', serializer.errors.get('non_field_errors', []))

    def test_custom_auth_token_serializer_missing_fields(self):
        # Test the serializer with missing fields
        data = {}
        serializer = CustomAuthTokenSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("This field is required.", serializer.errors.get("email", []))
        self.assertIn("This field is required.", serializer.errors.get("password", []))
        

    def test_custom_auth_token_serializer_blank_password(self):
        # Test the serializer with a blank password
        data = {
            'email': 'test@example.com',
            'password': '',
        }
        serializer = CustomAuthTokenSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("This field may not be blank.", serializer.errors.get('password', []))

    # Would add more test cases as needed.

class UserSerializerTest(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )

        # Create an API client for making requests
        self.client = APIClient()

    def test_user_serializer_valid(self):
        
        # TODO: Test for date joined
        # expected_date_joined = datetime.strptime(
        #     '2024-01-05T06:46:00.285323Z', '%Y-%m-%dT%H:%M:%S.%fZ'
        # ).replace(tzinfo=timezone.utc).isoformat()

        # Test the serializer with valid data
        serializer = UserSerializer(instance=self.user)
        
        expected_data = {
            "id": self.user.id,
            "username": "", 
            "email": "test@example.com", 
            "is_staff": False, 
            "is_active": True, 
            "groups": [], 
            "user_permissions": [], 
            "last_login": None, 
            "is_superuser": False, 
            "role": "customer", 
            "code": None
        }

        self.assertEqual(serializer.data, expected_data)


