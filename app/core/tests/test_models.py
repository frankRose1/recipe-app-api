from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successfull(self):
        """Test creating a new user with an email successfully"""
        params = {
            'email': 'test@local.host',
            'password': 'testPass123'
        }
        user = get_user_model().objects.create_user(**params)

        self.assertEqual(user.email, params['email'])
        self.assertTrue(user.check_password(params['password']))

    def test_new_user_email_normalized(self):
        """Test creating a new user will normalize the email"""
        email = 'test@LOCAL.HOST'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating a user with no email raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_super_user(self):
        """Test cresting a new super user"""
        user = get_user_model().objects.create_superuser(
            'superUser@local.host',
            'test123')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
