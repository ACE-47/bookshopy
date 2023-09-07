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

    productLiked = models.ManyToManyField(Product, related_name='items')

    

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
    @admin.display(ordering=['user__first_name'])
    def first_name(self):
        return self.user.first_name
    
    @admin.display(ordering=['user__last_name'])
    def last_name(self):
        return self.user.last_name
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']