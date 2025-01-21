from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from ..models import UserProfile
from django.urls import reverse

User = get_user_model()

class CustomAuthTokenViewTest(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )
        self.user.is_verified = True
        self.user.save()

        # Create an API client for making requests
        self.client = APIClient()

    def test_custom_auth_token_view(self):
        # Test the CustomAuthToken view with valid credentials
        url = reverse('authentication:token')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
        }

        response = self.client.post(url, data, format='json')

        

        # Verify that a new token is created for the user
        new_token = Token.objects.get(user=self.user)

        # Refetch user here to get the new auth token
        refetchUser = User.objects.get(id=self.user.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)
        self.assertEqual('test@example.com', response.data.get("email"))
        self.assertEqual(self.user.id, response.data.get("user_id"))
        self.assertEqual(self.user.id, response.data.get("user_id"))
        self.assertEqual(new_token.key, response.data.get("token"))

        self.assertEqual(response.data['token'], new_token.key)

    def test_custom_auth_token_view_invalid_credentials(self):
        # Test the CustomAuthToken view with invalid credentials
        url = reverse('authentication:token')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword',
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    # Would add more test cases as needed.


class CreateNewUserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='alreadyexistinguser@example.com',
            password='testpassword'
        )

        self.url = reverse("authentication:create_user")
        # Initialize an API client for making requests
        self.client = APIClient()

    def test_user_created_with_email_and_password(self):
        # New user data
        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
        }

        response = self.client.post(self.url, data, format="json")


        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user_id", response.data)
        self.assertIn("email", response.data)
        self.assertNotIn("token", response.data)
        self.assertIn("message", response.data)
        self.assertIn("role", response.data)

        self.assertEqual(response.data.get("message"), "A verification code has been sent to test@example.com.")
        self.assertEqual(response.data.get("role"), "customer")

    def test_blank_email(self):
        # New user data
        data = {
            'email': '',
            'password': 'pass',
        }
        response = self.client.post(self.url, data, format="json")
        self.assertIn("This field may not be blank.", response.data.get("email", []))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        # New user data
        # Email without @ symbol
        data = {
            'email': 'emailgmail.com',
            'password': 'goodpassword',
        }
        response = self.client.post(self.url, data, format="json")
        self.assertIn("Please enter a valid email address", response.data.get("email", []))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_password(self):
        # New user data
        data = {
            'email': 'email@gmail.com',
            'password': '',
        }
        response = self.client.post(self.url, data, format="json")
        self.assertIn("This field may not be blank.", response.data.get("password", []))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_too_short_and_common_password(self):
        # New user data
        data = {
            'email': 'email@gmail.com',
            'password': 'pass',
        }
        response = self.client.post(self.url, data, format="json")
        self.assertIn("This password is too short. It must contain at least 8 characters.", response.data.get("password", []))
        self.assertIn("This password is too common.", response.data.get("password", []))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_already_exists(self):
        # New user data
        data = {
            'email': 'alreadyexistinguser@example.com',
            'password': 'testpassword',
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("User with email already exists.", response.data.get("email", []))

        

class LogoutViewTest(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )

        # Create a token for the user
        # self.token = Token.objects.create(user=self.user)

        # Ensure user is verified
        self.user.is_verified = True
        self.user.save()

        # Create an API client for making requests
        self.client = APIClient()

    def test_logout_view_valid_token(self):
        # Test the logoutView with a valid token
        url = reverse('authentication:logout')
        headers = {'Authorization': f'Token {self.user.auth_token.key}'}

        response = self.client.post(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Logged out successfully.')

        # Verify that the token is deleted from the database
        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(key=self.user.auth_token.key)

    def test_logout_view_invalid_token(self):
        # Test the logoutView with an invalid token
        url = reverse('authentication:logout')
        headers = {'Authorization': 'Token invalid_token'}

        response = self.client.post(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Invalid token.')

    def test_logout_view_no_authorization_header(self):
        # Test the logoutView without an Authorization header
        url = reverse('authentication:logout')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    # Would add more test cases as needed.
        
class GetAndUpdateUserProfileDataTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )

        # Token is already created with user
        # In order to get the token, one must get it from the user

        # Ensure the user is verified
        self.user.is_verified = True
        self.user.save()

        self.auth_token = self.user.auth_token.key

        # Create an API client for making requests
        self.client = APIClient()

        self.url = reverse("authentication:profile")

        self.headers = {
            'Authorization': f"Token {self.auth_token}"
        }

    def test_get_user_profile_data(self):
        # Here a get request is sent to the api to fetch all the user profile data
        response = self.client.get(self.url, headers=self.headers)
        self.assertIn("email", response.data)
        self.assertIn("name", response.data)
        self.assertIn("date_of_birth", response.data)
        self.assertIn("permissions", response.data)
        self.assertIn("profile_picture", response.data)
        self.assertIn("bio", response.data)


    def test_update_user_profile_data(self):
        # Here a put request is sent to the api endpoint to 
        # partially update the profile data

        data = {
            "name": "Juliet",
            "date_of_birth": "1996-03-08",
            "phone_number": "08167930376",
            "bio": "This is my fantastic bio."
        }

        response = self.client.put(self.url, data, headers=self.headers)

        self.assertEqual("Juliet", response.data.get("name"))
        self.assertEqual("1996-03-08", response.data.get("date_of_birth"))
        self.assertEqual("08167930376", response.data.get("phone_number"))
        self.assertEqual("This is my fantastic bio.", response.data.get("bio"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)




