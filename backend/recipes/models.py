from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CASCADE, UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    """Тэги для рецептов: описываем 'name', 'color', 'slug'. """
    name = models.CharField(
        verbose_name='name_tag',
        max_length=200,
        unique=True,
        help_text='name tag',
    )
    color = models.CharField(
        verbose_name='HEX-код',
        max_length=7,
        unique=True,
        help_text='color',
    )
    slug = models.SlugField(
        verbose_name='slug',
        max_length=100,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель ингридиентов для рецепта: описываем 'name', 'measurement_unit'.
    """
    name = models.CharField(
        verbose_name='name_ingredient',
        max_length=150,
        help_text='name ingredient',
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=100,
        help_text='Выберите единицу измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Recipe(models.Model):
    """
    Модель приложения рецепта, описываем:
    'name', 'tags', 'ingredients',
    'image','cooking_time', 'pub_date', 'text'.
    """
    name = models.CharField(
        verbose_name='name_recipe',
        max_length=100,
        help_text='name recipe',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        help_text='ingredients',
        related_name='recipes',
        verbose_name='Ингредиент'
    )
    author = models.ForeignKey(
        User,
        verbose_name='author',
        related_name='recipes',
        on_delete=models.SET_NULL,
        help_text='Автор',
        null=True,
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='tag',
        related_name='recipes',
        help_text='tags',
    )
    image = models.ImageField(
        verbose_name='image_food',
        upload_to='recipes/image/',
        blank=True,
        help_text='Изображение с фотографией блюда',
    )
    text = models.TextField(
        verbose_name='Описание блюда',
        max_length=250,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=(
            MinValueValidator(
                1,
                'Блюдо готово!',
            ),
            MaxValueValidator(
                100,
                'Блюдо долго готовится!',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    """Модель связывает тэги с рецептами."""

    tag = models.ForeignKey(
        Tag,
        verbose_name="Тэги",
        on_delete=models.CASCADE,
        related_name="tag_recipes",
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="tag_recipes",
    )

    class Meta:
        verbose_name = "Тэг рецепта"
        verbose_name_plural = "Тэги рецептов"
        ordering = (
            "recipe__name",
            "tag__name",
        )
        constraints = (
            models.UniqueConstraint(
                fields=("tag", "recipe"),
                name="unique_tag_recipe_pair",
            ),
        )

    def __str__(self):
        return f"{self.id}: {self.recipe.name}, {self.tag.name}"


class IngredientRecipe(models.Model):
    """
    Модель связывает Recipe и Ingredient, описываем:
    'ingredient', 'recipe', 'amount'
    """
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ingredients',
        related_name='ingredient_to_recipe',
        on_delete=CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='recipes',
        related_name='recipe_to_ingredient',
        on_delete=CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='amount',
        default=0,
        validators=(
            MinValueValidator(
                1, 'Количество должно быть не меньше 1',
            ),
            MaxValueValidator(
                3000,
                'Достаточное количество ингридиентов!',
            ),
        ),
        help_text='amount_ingredient',
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_to_ingredient_exists')]
        ordering = ['-id']

    def __str__(self):
        return (f'{self.recipe}: {self.ingredient.name},'
                f' {self.amount}, {self.ingredient.measurement_unit}')


class Favorite(models.Model):
    """Класс избранных рецептов, описываем:
    'user', 'recipe'.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=CASCADE,
        verbose_name='Рецепт',
        related_name='favorite',
    )
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='Пользователь',
        related_name='favorited',
    )

    class Meta:
        verbose_name = 'Избранный рецепт',
        verbose_name_plural = 'Избранные рецепты пользователя'
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'user'),
                name='favorite_unique'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'


class Shopping(models.Model):
    """
    Модель рецептов в корзине покупок, описываем:
    'recipe', 'user'.
    """
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='recipes',
        related_name='shopping_cart',
        on_delete=CASCADE,
    )
    user = models.OneToOneField(
        User,
        verbose_name='users',
        related_name='shopping_cart',
        on_delete=CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('-id',)
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'user'),
                name='shopping_recipe_user_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Список покупок'
