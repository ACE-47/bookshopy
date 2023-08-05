from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

router = DefaultRouter()

router.register('products',views.ProductViewSet, basename='products')
router.register('collections',views.CollectionViewSet, basename='collections')
router.register('carts',views.CartViewSet, basename='carts')

product_router = routers.NestedDefaultRouter(router, 'products',lookup = 'product')
product_router.register('images', views.ProductImageViewSet, basename='product-images')

cart_router =routers.NestedDefaultRouter(router, 'carts', lookup = 'cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-item')

urlpatterns = router.urls + product_router.urls + cart_router.urls