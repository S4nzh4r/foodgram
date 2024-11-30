from django.db import models
from django.contrib.auth.models import AbstractUser

from .constants import EMAIL_LENGTH, MAX_LENGTH, ROLE_LENGTH


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    USER = 'user'
    ADMIN = 'admin'
    ROLE_USER = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор')
    ]
    username = models.CharField('Логин', max_length=MAX_LENGTH)
    first_name = models.CharField('Имя', max_length=MAX_LENGTH)
    last_name = models.CharField('Фамилия', max_length=MAX_LENGTH)
    email = models.EmailField(
        'E-mail Адрес пользователя', unique=True, max_length=EMAIL_LENGTH
    )
    role = models.CharField(max_length=ROLE_LENGTH, choices=ROLE_USER,
                            default=USER, verbose_name='Пользовательская роль')
    password = models.CharField(max_length=MAX_LENGTH, verbose_name='Пароль')
    avatar = models.ImageField(
        verbose_name='Аватар Пользователя',
        null=True,
        default=None,
        upload_to='user/images/'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    class Meta:
        """Класс Мета."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Описание пользователя."""
        return self.username
