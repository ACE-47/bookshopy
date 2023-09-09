from django.conf import settings
from django.contrib import admin
from django.db import models
from store.models import Product
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.


class LikedItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # contetn_object = GenericForeignKey()

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    

    

    def __str__(self):
        return self.user.username
    
    