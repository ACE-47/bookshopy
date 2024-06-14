from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

router = DefaultRouter()

router.register('products',views.ProductViewSet, basename='products')
router.register('products_advertize',views.ProductAdvertizeViewSet, basename='products-advertize')
router.register('collections',views.CollectionViewSet, basename='collections')
router.register('packages',views.PackageViewSet, basename='packages')
router.register('carts',views.CartViewSet, basename='carts')
router.register('customers',views.CustomerViewSet, basename='customers')
router.register('orders',views.OrderViewSet, basename='orders')
router.register('authors',views.AuthorModelViewSet, basename='authors')
router.register('promotions',views.PromotionsViewSet, basename='promotions')


product_router = routers.NestedDefaultRouter(router, 'products',lookup = 'product')
product_router.register('images', views.ProductImageViewSet, basename='product-images')

cart_router =routers.NestedDefaultRouter(router, 'carts', lookup = 'cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-item')

package_router = routers.NestedDefaultRouter(router, 'packages', lookup = 'package')
package_router.register('items', views.PackageItemViewSet, basename= 'package-items')


urlpatterns = router.urls + product_router.urls + cart_router.urls + package_router.urls