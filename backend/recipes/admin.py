from django.conf import settings
from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            Shopping, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    empty_value = settings.EMPTY_VALUE


@admin.register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('name',)
    empty_value = settings.EMPTY_VALUE


class IngredientRecipeInline(TabularInline):
    model = IngredientRecipe
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('author', 'name', 'cooking_time',
                    'get_tags', 'get_ingredients', 'favorite')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('pub_date', 'author', 'name', 'tags')
    inlines = (IngredientRecipeInline,)
    empty_value = settings.EMPTY_VALUE

    def get_ingredients(self, obj):
        return ', '.join([
            ingredients.name for ingredients
            in obj.ingredients.all()])

    get_ingredients.short_description = 'Ингридиенты'

    def favorite(self, obj):
        return obj.favorite.count()
    favorite.short_description = 'Избранное'

    def get_tags(self, obj):
        list_ = [_.name for _ in obj.tags.all()]
        return ', '.join(list_)


@admin.register(Shopping)
class ShoppingAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    empty_value = settings.EMPTY_VALUE


@admin.register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'get_recipe',)
    empty_value = settings.EMPTY_VALUE

    def get_recipe(self, obj):
        return [
            f'{item["name"]} ' for item in obj.recipe.values('name')[:10]]
