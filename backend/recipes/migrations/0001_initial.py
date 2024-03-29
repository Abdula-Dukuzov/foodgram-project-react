# Generated by Django 3.2.16 on 2023-04-11 18:03

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': ('Избранный рецепт',),
                'verbose_name_plural': 'Избранные рецепты пользователя',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name ingredient', max_length=150, verbose_name='name_ingredient')),
                ('measurement_unit', models.CharField(help_text='Выберите единицу измерения', max_length=100, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингридиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='IngredientRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=0, help_text='amount_ingredient', validators=[django.core.validators.MinValueValidator(1, 'Количество должно быть не меньше 1'), django.core.validators.MaxValueValidator(3000, 'Достаточное количество ингридиентов!')], verbose_name='amount')),
            ],
            options={
                'verbose_name': 'Ингридиент',
                'verbose_name_plural': 'Ингредиенты рецепта',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name recipe', max_length=100, verbose_name='name_recipe')),
                ('image', models.ImageField(blank=True, help_text='Изображение с фотографией блюда', upload_to='recipes/image/', verbose_name='image_food')),
                ('text', models.TextField(max_length=250, verbose_name='Описание блюда')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('cooking_time', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1, 'Блюдо готово!'), django.core.validators.MaxValueValidator(100, 'Блюдо долго готовится!')], verbose_name='Время приготовления')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name tag', max_length=200, unique=True, verbose_name='name_tag')),
                ('color', models.CharField(help_text='color', max_length=7, unique=True, verbose_name='HEX-код')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='TagRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tag_recipes', to='recipes.recipe', verbose_name='Рецепт')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tag_recipes', to='recipes.tag', verbose_name='Тэги')),
            ],
            options={
                'verbose_name': 'Тэг рецепта',
                'verbose_name_plural': 'Тэги рецептов',
                'ordering': ('recipe__name', 'tag__name'),
            },
        ),
        migrations.CreateModel(
            name='Shopping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to='recipes.recipe', verbose_name='recipes')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Список покупок',
                'ordering': ('-id',),
            },
        ),
    ]
