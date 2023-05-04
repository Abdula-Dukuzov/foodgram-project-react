from django.conf import settings
from django.contrib import admin
from django.contrib.admin import ModelAdmin, register
from django.contrib.auth import get_user_model

from users.models import Follow, User

User = get_user_model()


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('username', 'email', 'password', 'first_name')
    list_filter = ('first_name', 'email',)
    search_fields = ('username', 'email',)
    empty_value = settings.EMPTY_VALUE


@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ('user', 'author', 'created',)
    search_fields = ('user__email', 'user__email',)
    empty_value = settings.EMPTY_VALUE
