from django.contrib import admin

from .models import CustomUser


class UserAdmin(admin.ModelAdmin):
    """Админ-зона пользователя."""

    list_display = ('id', 'username', 'first_name',
                    'last_name', 'email', 'role', 'is_staff')
    list_editable = ('role', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


admin.site.register(CustomUser, UserAdmin)
