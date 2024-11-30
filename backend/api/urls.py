from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, RecipeViewSet, TagViewSet
from user.views import UserViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'auth/', include('djoser.urls.authtoken')),
]
