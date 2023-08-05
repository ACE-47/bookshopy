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



class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['id','']