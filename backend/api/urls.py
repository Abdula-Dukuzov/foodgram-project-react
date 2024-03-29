
from api.views import (DownloadShoppingCartView, IngredientViewSet,
                       RecipeShoppingViewSet, RecipeViewSet, TagViewSet,
                       UserViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, 'users')
router.register('tags', TagViewSet, 'tags')
router.register('recipes', RecipeViewSet, 'recipes')
router.register('recipes', RecipeShoppingViewSet, 'recipes')
router.register('ingredients', IngredientViewSet, 'ingredients')

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCartView.as_view(),
        name='download_shopping_cart',
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
