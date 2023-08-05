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
        
        return