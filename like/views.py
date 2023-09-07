from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import LikedItemSerializer
from .models import LikedItem
# Create your views here.


class LikedItemViewSet(ModelViewSet):
    # queryset = LikedItem.objects.all()
   
    serializer_class = LikedItemSerializer
    http_method_names = ['get','patch','post','delete','head','options']

    

    def get_queryset(self):
        user = self.request.user

        if user.is_staff :
            return LikedItem.objects.prefetch_related('productLiked').all()
        
        return LikedItem.objects.filter(user_id = user.id)
    

    