from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeDetailSerializer,
    RecipeImageSerializer
)


class BaseRecipeAttrViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for user's recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the currently authenticated user only"""
        queryset = self.queryset.filter(user=self.request.user)
        # see if client is requesting "assigned_only" tags/ingredients
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )

        if assigned_only:
            # get only the tags/ingredients assigned to a recipe
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.order_by('-name').distinct()

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
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    # create a custom action for creating an image, detail=True means it can
    # only be done for a specific image ==> /api/recipe/recipes/1/upload-image
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Custom action for uploading an image to a recipe"""
        # get the object being referenced by ID in the URL
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            # Perform a save on the recipe model
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
