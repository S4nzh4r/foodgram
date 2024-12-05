from django.contrib.auth.validators import UnicodeUsernameValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .constants import MAX_LENGTH
from recipe.models import Follow
from .models import CustomUser


class UserReadSerializer(serializers.ModelSerializer):
    """Класс Сеализатор Пользователей."""

    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Класс Мета."""

        model = CustomUser
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'username', 'avatar', 'is_subscribed'
        )
        extra_kwargs = {
            'is_subscribed': {'read_only': True}
        }

    def get_avatar(self, obj):
        """Возвращает ссылку на аватар."""
        if obj.avatar:
            return obj.avatar.url
        return None

    def get_is_subscribed(self, obj):
        """Метод на проверку подписки."""
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(user=user, author=obj).exists()
        return False


class UserSerializer(serializers.ModelSerializer):
    """Класс Сеализатор Пользователей."""

    username = serializers.CharField(
        max_length=MAX_LENGTH,
        validators=(
            UniqueValidator(
                queryset=CustomUser.objects.all()
            ),
            UnicodeUsernameValidator()
        )
    )

    class Meta:
        """Класс Мета."""

        model = CustomUser
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'username', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        """Метод создание записи пользователя."""
        return CustomUser.objects.create_user(**validated_data)


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сеализатор аватаров пользователей."""

    avatar = Base64ImageField()

    class Meta:
        """Класс Мета."""

        model = CustomUser
        fields = ('avatar',)
