from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test publicly available ingredients Api"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for this endpoint"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test private ingredients Api for authorized users"""
    def setUp(self):
        self.user = get_user_model().objects.create(
            email='testUser@local.host',
            password='testPass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Apple')
        Ingredient.objects.create(user=self.user, name='Orange')
        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test retrieving a list of ingredients"""
        user2 = get_user_model().objects.create(
            email='anotherUser@local.host',
            password='testPass'
        )
        Ingredient.objects.create(user=user2, name='Kale')
        Ingredient.objects.create(user=self.user, name='Celery')
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], 'Celery')

    def test_create_ingredient_success(self):
        """Test creating an ingredient is a success"""
        payload = {'name': 'Broccoli'}
        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            name=payload['name'],
            user=self.user
        ).exists()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating a tag with invalid input fails"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """
        Test that filtering by ingredients by those that are assigned to
        a recipe is successful. API accepts a param called "assigned_only"
        which will only retireve ingredients that are assigned to a recipe
        """
        ingredient1 = Ingredient.objects.create(user=self.user, name='Milk')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Butter')
        recipe = Recipe.objects.create(
            title='Chocolate Milkshake',
            time_minutes=2,
            price=2.50,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """
        Test that filtering ingredients by "assigned_only" returns a unique
        list of ingredients
        """
        ingredient = Ingredient.objects.create(user=self.user, name='Milk')
        Ingredient.objects.create(user=self.user, name='Butter')
        recipe1 = Recipe.objects.create(
            title='Chocolate Milkshake',
            time_minutes=2,
            price=2.50,
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Homemade Ice Cream',
            time_minutes=60,
            price=8.65,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
