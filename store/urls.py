from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

router = DefaultRouter()

router.register('products',views.ProductViewSet, basename='products')
router.register('collections',views.CollectionViewSet, basename='collections')
product_router = routers.NestedDefaultRouter(router, 'products',lookup = 'product')
product_router.register('images', views.ProductImageViewSet, basename='product-images')

urlpatterns = router.urls + product_router.urls