from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from recipe.serializers import TagSerializer


class TagsViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        """
        Override default method so that only the authenticated user's tags
        are returned.
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')
