from rest_framework import serializers
from .models import LikedItem
from store.serializers import SimpleProductSerializer
from store.models import Product

class LikedItemSerializer(serializers.ModelSerializer):
    productLiked = SimpleProductSerializer()
    class Meta:
        model = LikedItem
        fields = ['productLiked']


class AddLikedItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = LikedItem
        fields = ['product_id']


    def validate_product_id(self, value):
        if not Product.objects.filter(pk = value).exists():
            return serializers.ValidationError('No Product with the given ID was found!')

        return value


    def save(self, **kwargs):
        user_id = self.context['user_id']
        product_id = self.validated_data['product_id']

        product = Product.objects.get(pk = product_id )
        try:
            likedItem = LikedItem.objects.prefetch_related('productLiked').get(user_id = user_id, productLiked__id= product_id)
            print(likedItem)
            
            # likedItem.first().productLiked.clear()
            # self.instance = likedItem
        
        except LikedItem.DoesNotExist :
            
            likedItem = LikedItem.objects.create(user_id = user_id)
            print(likedItem.productLiked)
            
            self.instance = likedItem

            print(self.instance)        
        return self.instance
