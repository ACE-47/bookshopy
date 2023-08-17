from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin,DestroyModelMixin
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import IsAdminOrReadOnly
from .models import Product, ProductImage, OrderItem, Collection, Cart, CartItem, Customer, Order, Author, Promotion, ProductAdvertize
from . import serializers
from .filters import ProductFilter
from .paginations import ProductPagination

# Create your views here.
class PromotionsViewSet(ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = serializers.PromotionSerializer
    permission_classes = [IsAdminOrReadOnly]

class AuthorModelViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = serializers.authorSerializers
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        author = get_object_or_404(Author, pk=kwargs['pk'])
        if author.products.count() > 0:
            return Response({'error':'the Author can not be deleted because it is associated with products'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count = Count('products')).all()
    serializer_class = serializers.CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk = kwargs['pk'])
        if collection.products.count() > 0:
            return Response({'error':'Collection can not be deleted because it is associated with products'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        return super().destroy(request, *args, **kwargs)
    

class ProductViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.prefetch_related('images').select_related('publisher').all()
    serializer_class = serializers.ProdcutSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = ProductFilter
    search_fields = ['title', 'unit_price']
    ordering_fields = ['unit_price', 'last_update']


    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id = kwargs['pk']).count() > 0 :
            Response({'error': 'Product can not be deleted because it is associated with orderitems'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        return super().destroy(request, *args, **kwargs)



class ProductImageViewSet(ModelViewSet):
    serializer_class = serializers.ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    
    def get_queryset(self):
        return ProductImage.objects.filter(product_id = self.kwargs['product_pk'])
    

class ProductAdvertizeViewSet(ModelViewSet):
    queryset = ProductAdvertize.objects.all()
    serializer_class = serializers.ProductAdverSerializer

class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = serializers.CartSerializer

    
class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','delete','patch']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        
        elif self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        
        return serializers.CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}
    
    def get_queryset(self):
        return CartItem.objects.filter(cart_id = self.kwargs['cart_pk']).select_related('product')

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    permission_classes = [IsAdminUser]


# # maybe you change it 
#     def get_permissions(self):
#         if self.request.method == 'GET':
#             return[IsAdminUser()]
#         return [IsAuthenticated()]
        
    
    @action(detail = False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self,request):
        customer = Customer.objects.get(user_id = request.user.id)
        if request.method == 'GET':
            serializer = serializers.CustomerSerializer(customer)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = serializers.CustomerSerializer(customer,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        


class OrderViewSet(ModelViewSet):
    # queryset = Order.objects.all()
    # serializer_class = serializers.OrderSerializer
    http_method_names = ['get','patch','post','delete','head','options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateOrderSerializer
        
        elif self.request.method == 'PATCH':
            return serializers.UpdateOrderSerializer
        
        return serializers.OrderSerializer
    
    # def get_serializer_context(self):
    #     return {'user_id':self.request.user.id}
        

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related('items__product').order_by('-placed_at')
        
        customer_id = Customer.objects.only('id').get(user_id = user.id)
        return Order.objects.filter(customer_id = customer_id)
    

    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateOrderSerializer(data = request.data, context = {'user_id':self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data)

    
    
