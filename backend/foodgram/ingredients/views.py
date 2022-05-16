from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )
