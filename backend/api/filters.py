from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipe.models import Recipe, Tag


User = get_user_model()


class IngredientSearchFilter(SearchFilter):
    """Поисковый фильтр ингредиентов по имени."""

    search_param = 'name'


class RecipeFilter(FilterSet):
    """Фильтерсет рецептов.

    По тегам, авторам, избранным, в списке покупок.
    """

    author = filters.ModelChoiceFilter(
        queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart')
    is_favorited = filters.NumberFilter(
        method='filter_is_favorited')

    class Meta:
        """Класс Мета."""

        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Метод на фильтр избранный."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(favourite__author=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Метод на фильтр в списке покупок."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_carts__author=self.request.user)
        return queryset
