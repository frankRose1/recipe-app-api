from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='testUser@local.host', password='testPass'):
    """
    Create and return a sample user

    :param email: Email address
    :type email: str
    :param password: Password
    :type password: str
    :return: User model instance
    """
    return get_user_model().objects.create(email=email, password=password)


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

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the ingredient string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and Mushroom Sauce',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        expected_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, expected_path)
