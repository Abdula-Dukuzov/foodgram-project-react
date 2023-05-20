from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Ingredient, IngredientRecipe, Recipe, Shopping,
                            Tag, TagRecipe)
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.generics import get_object_or_404
from users.models import Follow, User

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для модели User.
    """
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'password',
        )


class UserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Провоеряем подписанны пользователи.
        """
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class FollowShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для короткой модели рецепта
    для избранных рецептов в подписках.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода подписок у авторов.
    """
    recipes = FollowShortRecipeSerializer(many=True, read_only=True)
    is_subscribed = SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True)

    class Meta:
        model = Follow
        fields = ('is_subscribed', 'recipes', 'recipes_count',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return obj.following.filter(user=user, author=obj).exists()

    def validate(self, data):
        request = self.context['request']
        author = self.initial_data['author']
        if request.user == author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на себя.'})
        if request.user.follower.filter(author=author).exists():
            raise serializers.ValidationError({'errors': 'Есть подписка.'})
        return data


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тэгов.
    """
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов и рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для работы и просмотра рецепта """
    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, )
    ingredients = SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=user).exists()


class TagRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализтор для вывода тэгов в рецепте.
    """

    class Meta:
        model = TagRecipe
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("id", "name", "color", "slug",)

    def to_internal_value(self, data):
        if isinstance(data, int):
            return get_object_or_404(Tag, pk=data)
        return data


class RecipeAddSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления рецептов.
    """
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления еды должно быть не меньше одной минуты.'
            )
        return cooking_time

    def validate_ingredients(self, ingredients):
        ingredient_ids = set()
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными.'
                )
            if amount <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше нуля.'
                )
            ingredient_ids.add(ingredient_id)
        return ingredients

    def validate_tags(self, tags):
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError('Тег отсутствует.')
        return tags

    def validate(self, attrs):
        attrs = super().validate(attrs)
        ingredients = attrs.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError('Отсутствуют ингредиенты.')
        return attrs

    def create(self, validated_data):
        request = self.context.get('request', None)
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        IngredientRecipe.objects.filter(recipe=instance).delete()

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            IngredientRecipe.objects.create(
                recipe=instance, ingredient=ingredient, amount=amount
            )

        instance.tags.set(tags)

        return super().update(instance, validated_data)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shopping_cart.filter(user=request.user).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            data['is_favorited'] = self.get_is_favorited(instance)
            data['is_in_shopping_cart'] = self.get_is_in_shopping_cart(
                instance)
        else:
            data['is_favorited'] = False
            data['is_in_shopping_cart'] = False
        return data


class ShortRecipeShoppingSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения сведений о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    """
    Сериализатор вывода авторов на которых подписан текущий пользователь.
    """
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author_id = self.context.get(
            'request').parser_context.get('kwargs').get('id')
        author = get_object_or_404(User, id=author_id)
        user = self.context.get('request').user
        if user.follower.filter(author=author_id).exists():
            raise ValidationError(
                detail='Подписка уже существует!',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = ShortRecipeShoppingSerializer(recipes, many=True, read_only=True)
        return serializer.data


class ShoppingSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок """

    class Meta:
        model = Shopping
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        if Shopping.objects.filter(user=user,
                                   recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeShoppingSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
