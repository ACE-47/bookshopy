from rest_framework import serializers
from .models import LikedItem
from store.serializers import SimpleProductSerializer

class LikedItemSerializer(serializers.ModelSerializer):
    productLiked = SimpleProductSerializer(many = True)
    class Meta:
        model = LikedItem
        fields = ['user','productLiked']
