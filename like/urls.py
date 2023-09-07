

from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import LikedItemViewSet


router = DefaultRouter()
router.register('likedItem',LikedItemViewSet, basename='likedItem')


urlpatterns = router.urls
