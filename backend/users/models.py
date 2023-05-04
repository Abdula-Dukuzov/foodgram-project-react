from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(
        'Email',
        max_length=200,
        unique=True,
    )
    password = models.CharField(
        'password',
        max_length=150,
    )
    username = models.CharField(
        verbose_name=_('username'),
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Пользователь с username существует'
        )],
        help_text=_('Укажите username'),
    )
    first_name = models.CharField(
        'Имя',
        max_length=150)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('last_name',)

    def __str__(self):
        return self.email


class Follow(models.Model):
    """
    Модель подписки пользователей друг на друга, описываем:
    'author', 'user', 'created'.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='author',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True)

    class Meta:
        ordering = ['user']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follower')
        ]

    def __str__(self):
        return f'{self.user} - {self.author}'
