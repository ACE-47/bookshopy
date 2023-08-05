from rest_framework import serializers
from . import models


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



class ProdcutSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many = True, read_only = True)
    class Meta:
        model = models.Product
        fields = ['id','title','description','slug','inventory','unit_price','collection','images']


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id','title','unit_price']

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