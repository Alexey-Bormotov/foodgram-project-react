import os

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Favorite, Recipe, RecipeIngredients, ShoppingCart
from .permissions import IsAuthorOrAdminPermission
from .serializers import (RecipeSerializer,
                          RecipeCreateUpdateSerializer,
                          ShortRecipeSerializer)

from ingredients.models import Ingredient
from users.pagination import CustomPageNumberPagination


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer

        return RecipeSerializer

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            if Favorite.objects.all().filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError('Рецепт уже в избранном.')

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Favorite.objects.all().filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    'Рецепта нет в избранном, либо он уже удален.'
                )

            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
            favorite.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            if ShoppingCart.objects.all().filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    'Рецепт уже в списке покупок.'
                )

            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not ShoppingCart.objects.all().filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    'Рецепта нет в списке покупок, либо он уже удален.'
                )

            shopping_cart = get_object_or_404(
                ShoppingCart,
                user=user,
                recipe=recipe
            )
            shopping_cart.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.all().filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy_list = RecipeIngredients.objects.all().filter(
            recipe__in=recipes
        ).values(
            'ingredient'
        ).annotate(
            amount=Sum('amount')
        )

        filename = f'{self.request.user.username}_buy_list.txt'

        if not os.path.isdir('media/buy_lists'):
            os.mkdir('media/buy_lists')

        with open(f'media/buy_lists/{filename}', 'w') as textfile:
            textfile.write('Список покупок с сайта Foodgram:\n\n')

            for item in buy_list:
                ingredient = Ingredient.objects.get(pk=item['ingredient'])
                amount = item['amount']
                textfile.write(
                    f'{ingredient.name}, {amount} '
                    f'{ingredient.measurement_unit}\n'
                )

        with open(f'media/buy_lists/{filename}', 'r') as textfile:
            response = HttpResponse(textfile.read(), content_type="text/txt")
            response['Content-Disposition'] = (
                'attachment; filename=' + filename
            )

        return response
