from django.shortcuts import render
from requests import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import LikedItemSerializer, AddLikedItemSerializer
from .models import LikedItem
# Create your views here.


class LikedItemViewSet(ModelViewSet):
    # queryset = LikedItem.objects.all()
    
    # serializer_class = LikedItemSerializer
    http_method_names = ['get','post','head','options']

    

    def get_queryset(self):
        user = self.request.user

        if user.is_staff :
            return LikedItem.objects.select_related('product').all()
        
        return LikedItem.objects.select_related('product').prefetch_related('product__images').select_related('product__publisher').select_related('product__auther').select_related('product__collection').prefetch_related('product__promotions').filter(user_id = user.id)
    

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddLikedItemSerializer
        
        return LikedItemSerializer
    
    def get_serializer_context(self):
        return {'user_id':self.request.user.id}
    
    
    # def create(self, request, *args, **kwargs):
    #     serializer = AddLikedItemSerializer.create(data = request.data, context= {'user_id':self.request.user.id})
    #     serializer.is_valid(raise_exception=True)
    #     itemLiked = serializer.save()
    #     serializer = LikedItemSerializer(itemLiked)
    #     return Response(serializer.data)
    



    