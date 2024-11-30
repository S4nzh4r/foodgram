from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

from .constants import MAX_LENGTH, MIN_VALUE, SLUG_LENGTH

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Продукт', max_length=MAX_LENGTH
    )

    measurement_unit = models.CharField(
        verbose_name='Единица измерения', max_length=MAX_LENGTH
    )

    class Meta:
        """Класс Мета."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        """Описание ингредиента."""
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Модель Тег."""

    name = models.CharField(
        verbose_name='Название Тега', max_length=MAX_LENGTH
    )

    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=SLUG_LENGTH,
        unique=True
    )

    class Meta:
        """Класс Мета."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Описание тега."""
        return f'{self.name}'


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        verbose_name='Название', max_length=MAX_LENGTH
    )

    author = models.ForeignKey(
        User, verbose_name='Автор рецепта',
        related_name='recipes', on_delete=models.CASCADE
    )

    tags = models.ManyToManyField(
        Tag, verbose_name='Тег', related_name='recipes'
    )

    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты',
        through='RecipeIngredient'
    )

    image = models.ImageField(
        verbose_name='Рисунок',
        upload_to='recipes/images/'
    )

    text = models.TextField(
        verbose_name='Текст рецепта'
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(
            MIN_VALUE,
            message=(
                f'Минимальное время в минутах'
                f'не должно быть меньше {MIN_VALUE}'
            )
        )]
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикаций', auto_now_add=True
    )

    short_code = models.CharField(max_length=6,
                                  unique=True,
                                  blank=True,
                                  null=True)

    class Meta:
        """Класс Мета."""

        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_author_recipe'
            ),
        )

    def __str__(self):
        """Описание рецепта."""
        return (f'{self.name} '
                f'Автор: {self.author.first_name} {self.author.last_name}')


class RecipeIngredient(models.Model):
    """Вспомогательная таблица ингредиентов и рецетов."""

    ingredients = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )

    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт',
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )

    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                MIN_VALUE, f'Минимальное количество ингредиентов {MIN_VALUE}'
            )],
        verbose_name='Количество',
        help_text='Укажите количество ингредиента')

    class Meta:
        """Класс Мета."""

        verbose_name = 'Рецепт Ингредиент'
        verbose_name_plural = 'Рецепт Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredients'),
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        """Описание рецепт ингредиентов."""
        return f'{self.recipe}, {self.ingredients}'


class ShoppingCart(models.Model):
    """Модель для списка покупок."""

    author = models.ForeignKey(
        User, verbose_name='Автор',
        related_name='shopping_carts', on_delete=models.CASCADE
    )

    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт',
        related_name='shopping_carts', on_delete=models.CASCADE
    )

    class Meta:
        """Класс Мета."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_shopping_author_recipe'
            ),
        )

    def __str__(self):
        """Описание списка покупок."""
        return f'список для {self.recipe}'


class Favourite(models.Model):
    """Модель для избранных рецептов."""

    author = models.ForeignKey(
        User, verbose_name='Автор',
        related_name='favourite', on_delete=models.CASCADE
    )

    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт',
        related_name='favourite', on_delete=models.CASCADE
    )

    class Meta:
        """Класс Мета."""

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_favourite_author_recipe'
            ),
        )

    def __str__(self):
        """Описание избранных рецептов."""
        return f'Избранный {self.recipe}'


class Follow(models.Model):
    """Подписки на авторов рецептов."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='follower',
        on_delete=models.CASCADE,
        help_text='Текущий пользователь')
    author = models.ForeignKey(
        User,
        verbose_name='Подписка',
        related_name='followed',
        on_delete=models.CASCADE,
        help_text='Подписаться на автора рецепта')

    class Meta:
        """Класс Мета."""

        verbose_name = 'Моя подписка'
        verbose_name_plural = 'Мои подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following'),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_following')]

    def __str__(self):
        """Описание подписок."""
        return f'Пользователь {self.user} подписан на {self.author}'
