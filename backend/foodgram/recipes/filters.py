from django_filters import rest_framework
from distutils.util import strtobool

from .models import Favorite, Recipe, ShoppingCart
from tags.models import Tag

CHOICES_LIST = (
    ('0', 'False'),
    ('1', 'True'),
)


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_favorited_method'
    )
    is_in_shopping_cart = rest_framework.ChoiceFilter(
        choices=CHOICES_LIST,
        method='is_in_shopping_cart_method'
    )
    author = rest_framework.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def is_favorited_method(self, queryset, name, value):
        favorites = Favorite.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in favorites]
        new_queryset = Recipe.objects.filter(id__in=recipes)

        if not strtobool(value):
            new_queryset = queryset.difference(new_queryset)

        return new_queryset

    def is_in_shopping_cart_method(self, queryset, name, value):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        new_queryset = Recipe.objects.filter(id__in=recipes)

        if not strtobool(value):
            new_queryset = queryset.difference(new_queryset)

        return new_queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
