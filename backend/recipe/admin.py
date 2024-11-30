from django.contrib import admin

from .models import (Favourite,
                     Follow,
                     Ingredient,
                     RecipeIngredient,
                     Recipe,
                     ShoppingCart,
                     Tag)


class IngredientsInline(admin.StackedInline):
    """Админ-зона для интеграции добавления ингридиентов в рецепты.

    Сразу доступно добавление 3х ингрдиентов.
    """

    model = RecipeIngredient
    extra = 2


class FollowAdmin(admin.ModelAdmin):
    """Админ-зона подписок."""

    list_display = ('user', 'author')
    list_filter = ('author',)
    search_fields = ('user',)


class FavoriteAdmin(admin.ModelAdmin):
    """Админ-зона избранных рецептов."""

    list_display = ('author', 'recipe')
    list_filter = ('author',)
    search_fields = ('author',)


class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-зона покупок."""

    list_display = ('author', 'recipe')
    list_filter = ('author',)
    search_fields = ('author',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админ-зона ингридентов для рецептов."""

    list_display = ('id', 'recipe', 'ingredients', 'amount',)
    list_filter = ('recipe', 'ingredients')
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """Админ-зона рецептов.

    Добавлен просмотр кол-ва добавленных рецептов в избранное.
    """

    list_display = ('id', 'author', 'name', 'pub_date', 'in_favorite_count')
    search_fields = ('name', 'author')
    list_filter = ('pub_date', 'author', 'tags')
    filter_horizontal = ('ingredients', 'tags')
    inlines = [IngredientsInline]

    def in_favorite_count(self, obj):
        """Число добавленных в избранное рецепта."""
        return obj.favourite.all().count()


class TagAdmin(admin.ModelAdmin):
    """Админ-зона тегов."""

    list_display = ('id', 'name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    """Админ-зона ингридиентов."""

    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.empty_value_display = 'Не задано'
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Favourite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
