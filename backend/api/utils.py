"""Файл доп функций."""
import secrets

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


def generate_unique_short_code(model, recipe):
    """Метод для генераций уникального кода."""
    pk = recipe.pk
    while True:
        short_code = secrets.token_hex(3)[:6]
        if not model.objects.filter(pk=pk, short_code=short_code).exists():
            return short_code


def action_method(model, serializer_class, **kwargs):
    """Метод для action методов в RecipeViewSet."""
    recipe = kwargs.get('recipe')
    user = kwargs.get('user')
    request = kwargs.get('request')
    name = kwargs.get('name')

    if request.method == 'POST':
        if model.objects.filter(recipe=recipe, author=user).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=user, recipe=recipe)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    if model.objects.filter(recipe=recipe, author=user).exists():
        obj = get_object_or_404(model, recipe=recipe, author=user)
        obj.delete()
        return Response(f'Рецепт успешно удалён из {name}.',
                        status=status.HTTP_204_NO_CONTENT)
    return Response({'errors': 'Объект не найден'},
                    status=status.HTTP_400_BAD_REQUEST)
