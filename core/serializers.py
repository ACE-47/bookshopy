from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework import serializers

class UserCreateSerializer(BaseUserCreateSerializer):
    # email = serializers.EmailField()
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id','username','password','email','first_name','last_name']



class UserSerializer(BaseUserSerializer):
    email = serializers.EmailField(required = True)
    class Meta(BaseUserSerializer.Meta):

        fields = ['id', 'username', 'email','first_name', 'last_name']