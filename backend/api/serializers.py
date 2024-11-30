"""Работа сеализаторов рецептов."""
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipe.constants import MIN_VALUE
from recipe.models import (Favourite,
                           Follow,
                           Ingredient,
                           Recipe,
                           RecipeIngredient,
                           ShoppingCart,
                           Tag)
from user.serializers import Base64ImageField, UserReadSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сеализатор Ингредиентов."""

    class Meta:
        """Класс Мета."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сеализатор Тега."""

    class Meta:
        """Класс Мета."""

        model = Tag
        fields = ('id', 'name', 'slug')


class BaseSerializer(serializers.ModelSerializer):
    """Базовый класс сеализатор для избранных и списка покупок сеализаторов."""

    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True
    )

    class Meta:
        """Класс Мета."""

        fields = ('id', 'name', 'image', 'cooking_time')


class FavouriteSerializer(BaseSerializer):
    """Сеализатор для избранных рецептов."""

    class Meta(BaseSerializer.Meta):
        """Класс Мета."""

        model = Favourite


class ShoppingCartSerializer(BaseSerializer):
    """Класс сеализатор списка покупок."""

    class Meta(BaseSerializer.Meta):
        """Класс Мета."""

        model = ShoppingCart


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сеализатор для связанной модели."""

    id = serializers.ReadOnlyField(
        source='ingredients.id')
    name = serializers.ReadOnlyField(
        source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')

    class Meta:
        """Класс Мета."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый класс Рецетов."""

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Класс Мета."""

        model = Recipe
        fields = (
            'id', 'name', 'tags', 'ingredients',
            'image', 'author', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        """Метод поля на проверку в избранное."""
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favourite.objects.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Метод поля на проверку в списке покупок."""
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(recipe=obj).exists()
        return False


class RecipeReadSerializer(BaseRecipeSerializer):
    """Сеализатор для чтения Рецептов."""

    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    author = UserReadSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сеализатор для создание ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_VALUE)

    class Meta:
        """Класс Мета."""

        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(BaseRecipeSerializer):
    """Сеализатор для записи рецептов."""

    ingredients = AddIngredientSerializer(
        many=True, write_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=True)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    cooking_time = serializers.IntegerField(min_value=MIN_VALUE)

    class Meta(BaseRecipeSerializer.Meta):
        """Класс Мета."""

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author'),
                message='Рецепт уже добавлен!'
            ),
        )

    def validate_ingredients(self, value):
        """Валидация поля ингредиентов."""
        ingredients = value

        if not ingredients:
            raise ValidationError('Выберите ингредиенты.')

        ingredient_list = []

        for ingredient in ingredients:
            item = get_object_or_404(Ingredient, name=ingredient.get('id'))
            if item in ingredient_list:
                raise ValidationError('Ингредиенты повторяются!')

            if int(ingredient.get('amount')) <= 0:
                raise ValidationError('Количество должно быть больше нуля!')

            ingredient_list.append(item)

        return value

    def validate_tags(self, value):
        """Валидация тегов."""
        tags = value

        if not tags:
            raise ValidationError('Нужно выбрать тег!')

        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError('Теги не должны повторятся!')

            tags_list.append(tag)
        return value

    def add_tags_ingredients(self, ingredients, tags, recipe):
        """Метод для добавление записи тегов и ингредиентовв модели."""
        for ingredient in ingredients:
            RecipeIngredient.objects.update_or_create(
                recipe=recipe,
                ingredients=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        recipe.tags.set(tags)

    def create(self, validated_data):
        """Метод создания записи."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self.add_tags_ingredients(ingredients, tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления записи."""
        if ('ingredients' not in self.initial_data
                or 'tags' not in self.initial_data):
            raise ValidationError('Поле ингредиенты и теги обязательны!')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.add_tags_ingredients(ingredients, tags, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Метод для вывода данных."""
        recipe = super().to_representation(instance)
        recipe['ingredients'] = RecipeIngredientSerializer(
            instance.recipe_ingredients.all(), many=True).data
        recipe['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        recipe['author'] = UserReadSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data
        return recipe


class RecipeAuthorSerializer(serializers.ModelSerializer):
    """Сеализатор для вывода рецептов подписок."""

    class Meta:
        """Класс Мета."""

        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)


class FollowSerializer(serializers.ModelSerializer):
    """Сеализатор для Подписок."""

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        """Класс Мета."""

        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count', 'avatar')

    def get_avatar(self, obj):
        """Метод получения ссылки аватара."""
        avatar_url = obj.author.avatar
        if avatar_url:
            return avatar_url.url
        return None

    def get_is_subscribed(self, obj):
        """Метод на проверку подписки."""
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(
                user=obj.user,
                author=obj.author).exists()
        return False

    def get_recipes(self, obj):
        """Метод для получения рецептов подписки."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeAuthorSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Метод подсчёта рецептов подписки."""
        return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
        """Метод валидация полей."""
        author = self.context.get('author')
        user = self.context.get('request').user
        if Follow.objects.filter(
                author=author,
                user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST)
        return data
