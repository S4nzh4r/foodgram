from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from api.pagination import CustomPagination
from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsOwnerOrAdminOrReadOnly
from recipe.models import (
    Favourite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from .serializers import (FavouriteSerializer,
                          IngredientSerializer,
                          RecipeReadSerializer,
                          RecipeWriteSerializer,
                          ShoppingCartSerializer,
                          TagSerializer)
from .utils import action_method, generate_unique_short_code


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вьюсет Тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (IngredientSearchFilter, )
    # Поиск с символом в поле оказывается не работает на sqlite3
    search_fields = ('@name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет Рецептов."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        """Метод установки класс сеализатора."""
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True,
            methods=['get', ],
            url_path='get-link',
            permission_classes=[AllowAny, ])
    def get_link(self, request, pk=None):
        """Метод для получения короткой ссылки."""
        recipe = self.get_object()
        base_url = settings.BASE_URL
        short_code = generate_unique_short_code(Recipe, recipe)
        recipe.short_code = short_code
        recipe.save()
        short_link = f'{base_url}/r/{short_code}/'
        return Response({'short-link': short_link}, status=200)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, *args, **kwargs):
        """Метод для добавления избранного."""
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        user = self.request.user
        response = action_method(Favourite,
                                 FavouriteSerializer,
                                 recipe=recipe,
                                 user=user,
                                 request=request,
                                 name='Избранный')
        return response

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, *args, **kwargs):
        """Метод для добавления в список покупок."""
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        user = self.request.user
        response = action_method(ShoppingCart,
                                 ShoppingCartSerializer,
                                 recipe=recipe,
                                 user=user,
                                 request=request,
                                 name='Список Покупок')
        return response

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request, *args, **kwargs):
        """Метод для скачивания списка покупок."""
        shopping_cart_items = (ShoppingCart
                               .objects
                               .filter(author=request.user)
                               .select_related('recipe'))
        if not shopping_cart_items.exists():
            return HttpResponse('Your shopping cart is empty.',
                                content_type='text/plain')

        shopping_list = {}
        for item in shopping_cart_items:
            ingredients = RecipeIngredient.objects.filter(recipe=item.recipe)
            for ingredient in ingredients:
                key_name = (f'* {ingredient.ingredients.name} '
                            f'({ingredient.ingredients.measurement_unit}) -')
                if shopping_list.get(key_name, None):
                    shopping_list[key_name] += ingredient.amount
                    continue
                shopping_list[key_name] = ingredient.amount

        file_content = 'Список покупок: \n'
        for ingredient, amount in shopping_list.items():
            file_content += f'{ingredient} {amount} \n'
        filename = 'shopping_list.txt'

        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response


def redirect_from_short_link(request, short_code):
    """Вью функция для переадресаций от короткой ссылки."""
    try:
        recipe = get_object_or_404(Recipe, short_code=short_code)
        base_url = settings.BASE_URL
        return redirect(f'{base_url}/recipes/{recipe.pk}')
    except Exception:
        return HttpResponseNotFound('Ошибка в ссылке!')
