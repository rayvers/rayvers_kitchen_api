from django.test import TestCase
from ..helpers import is_valid_email, check_email, is_valid_password

class HelpersTestCase(TestCase):

    def test_is_valid_email_valid(self):
        # Test a valid email
        valid_email = "test@example.com"
        self.assertTrue(is_valid_email(valid_email))

    def test_is_valid_email_invalid(self):
        # Test an invalid email
        invalid_email = "invalid_email"
        self.assertFalse(is_valid_email(invalid_email))

    def test_check_email_valid(self):
        # Test check_email function with a valid email
        valid_email = "test@example.com"
        result = check_email(valid_email)
        self.assertTrue(result.status)
        self.assertEqual(result.message, "Valid email")

    def test_check_email_invalid(self):
        # Test check_email function with an invalid email
        invalid_email = "invalid_email"
        result = check_email(invalid_email)
        self.assertFalse(result.status)
        self.assertEqual(result.message, "Invalid email")
        self.assertIn("Please enter a valid email address", result.error_messages)

    def test_is_valid_password_valid(self):
        # Test a valid password
        valid_password = "StrongPassword123!"
        result = is_valid_password(valid_password)
        self.assertTrue(result.status)
        self.assertEqual(result.message, "Valid password")

    def test_is_valid_password_invalid(self):
        # Test an invalid password
        invalid_password = "weak"
        result = is_valid_password(invalid_password)
        self.assertFalse(result.status)
        self.assertEqual(result.message, "Invalid password")
        self.assertIn("This password is too short. It must contain at least 8 characters.", result.error_messages)
