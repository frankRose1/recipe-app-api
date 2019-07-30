from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeDetailSerializer
)


class BaseRecipeAttrViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for user's recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the currently authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Override default behavior so that user attribute on the object being
        created can be set to the currently authenticated user
        """
        serializer.save(user=self.request.user)


class TagViewset(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewset(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


# ModelViewset allows users to perform all CRUD opertaions
class RecipeViewset(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    def _params_to_ints(self, qs):
        """
        Convert a list of string IDs to a list of integers

        :param qs: Query string of comma separated ID's sent in request
        :type qs: str
        :return: list
        """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Limit queryset results to only the authenticated user"""
        tags_qs = self.request.query_params.get('tags')
        ingredients_qs = self.request.query_params.get('ingredients')
        queryset = self.queryset.filter(user=self.request.user)

        if tags_qs:
            tag_ids = self._params_to_ints(tags_qs)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients_qs:
            ingredient_ids = self._params_to_ints(ingredients_qs)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset

    def get_serializer_class(self):
        """
        Return the appropriate serializer class so that the detail
        serializer is used when retrieving a single record
        """
        if self.action == 'retrieve':
            return RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)
