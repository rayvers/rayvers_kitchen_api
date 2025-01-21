from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import UserProfile


User = get_user_model()

class UsersManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email="normal@user.com", password="foo")
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email="super@user.com", password="foo")
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com", password="foo", is_superuser=False)
            




class UserProfileModelTest(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(email='test@example.com', password='testpassword')

        # Create a client for making requests
        self.client = Client()

    def test_user_profile_creation(self):
        # Check if the UserProfile is created when a User is created
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_user_profile_str_method(self):
        # Check the __str__ method of UserProfile
        expected_str = f"{self.user.email}'s profile"
        self.assertEqual(str(self.user.profile), expected_str)

    def test_get_image_url_property(self):
        # Check the get_image_url property
        self.user.profile.image_url = 'path/to/image.jpg'
        expected_url = self.user.profile.image_url
        self.assertEqual(self.user.profile.get_image_url, expected_url)

    def test_create_token_signal(self):
        # Check if a UserProfile is created when a User is created using the signal
        new_user = get_user_model().objects.create(email='newuser@example.com', password='newuserpassword')
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())

    def test_user_profile_update(self):
        # Test updating UserProfile fields
        updated_name = 'Updated User'
        updated_bio = 'This is an updated bio.'

        self.user.profile.name = updated_name
        self.user.profile.bio = updated_bio
        self.user.profile.save()

        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.name, updated_name)
        self.assertEqual(updated_profile.bio, updated_bio)

    # Would more test cases as needed based on requirements.