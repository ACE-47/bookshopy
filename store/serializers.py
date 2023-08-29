from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from . import models

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id','title','unit_price']


class authorSerializers(serializers.ModelSerializer):
    products = SimpleProductSerializer(many =True)
    class Meta:
        model = models.Author
        fields = ['id' ,'name', 'about', 'birth_date', 'products','author_image']


    def get_products(self,author:models.Author):
        return models.Product.objects.prefetch_related('products').filter(auther_id = author.pk)[:5]


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only = True)
    class Meta:
        model = models.Collection
        fields = ['id','title', 'products_count']

    

class ProductImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.ProductImage
        fields = ['id', 'image']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return models.ProductImage.objects.create(product_id = product_id, **validated_data)


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Publisher
        fields = ['id', 'name']


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Promotion
        fields = ['id', 'title', 'descriptions', 'discount',]

class SimpleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = ['id', 'name']

class ProdcutSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many = True, read_only = True)
    publisher = PublisherSerializer( read_only = True)
    auther = SimpleAuthorSerializer()

    class Meta:
        model = models.Product
        fields = ['id','title','descriptions','slug', 'inventory','unit_price','collection','publisher','auther','images', 'promotions']

    # def get_auther(self, author:models.Author):
    #     return author.name & author.id
        # return 0
    


class ProductAdverSerializer(serializers.ModelSerializer):
    product = ProdcutSerializer()
    class Meta: 
        model = models.ProductAdvertize
        fields =['product']




class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = models.CartItem
        fields = ['id','product','quantity','total_price']

    def get_total_price(self, cartItem:models.CartItem):
        return cartItem.quantity * cartItem.product.unit_price

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only = True)
    items = CartItemSerializer(many = True, read_only = True)
    total_cart_price = serializers.SerializerMethodField()
    class Meta:
        model = models.Cart
        fields = ['id', 'items','total_cart_price']

    def get_total_cart_price(self, cart:models.Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
        

class AddCartItemSerializer(serializers.ModelSerializer):

    product_id = serializers.IntegerField()
    class Meta:
        model = models.CartItem
        fields = ['id', 'product_id', 'quantity']

    def validate_product_id(self, value):
        if not models.Product.objects.filter(pk = value).exists():
            return serializers.ValidationError('No Product with the given ID was found!')
        return value
    
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cartitem = models.CartItem.objects.get(cart_id = cart_id, product_id = product_id)
            cartitem.quantity += quantity
            cartitem.save()
            self.instance = cartitem
        except models.CartItem.DoesNotExist:
            cartitem = models.CartItem.objects.create(cart_id = cart_id, **self.validated_data)
            self.instance = cartitem
        
        return self.instance


        return super().save(**kwargs)
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only = True)
    class Meta:
        model =models.Customer
        fields = ['id', 'user_id', 'phone', 'birth_date']
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(many = True)
    class Meta:
        model = models.OrderItem
        fields = ['product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many = True)
    class Meta:
        model = models.Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']
        


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['payment_status']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not models.Cart.objects.filter(pk = cart_id).exists():
            raise serializers.ValidationError('No Cart with the given ID was Found')
        
        if models.CartItem.objects.filter(cart_id = cart_id).count() == 0:
            raise serializers.ValidationError('the current Cat is Empty')

    
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            
            customer = models.Customer.objects.get(user_id = user_id)
            order = models.Order.objects.create(customer = customer)

            cartItems = models.CartItem.objects.select_related('product').filter(cart_id = cart_id)

            orderItems = [models.OrderItem(
                            order = order,
                            product = item.product,
                            unit_price = item.product.unit_price,
                            quantity = item.quantity,
                            ) for item in cartItems]

            models.OrderItem.objects.bulk_create(orderItems)
            models.Cart.objects.filter(pk = cart_id).delete()
            return order
