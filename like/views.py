from django.shortcuts import render
from requests import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import LikedItemSerializer, AddLikedItemSerializer
from .models import LikedItem
# Create your views here.


class LikedItemViewSet(ModelViewSet):
    # queryset = LikedItem.objects.all()
    
    serializer_class = LikedItemSerializer
    # http_method_names = ['get','patch','post','delete','head','options']

    

    def get_queryset(self):
        user = self.request.user

        if user.is_staff :
            return LikedItem.objects.select_related('productLiked').all()
        
        return LikedItem.objects.select_related('productLiked').filter(user_id = user.id)
    

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
    



    