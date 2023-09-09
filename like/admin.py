from django.contrib import admin
from django.contrib.admin import TabularInline
# from store.models import Product
from .models import LikedItem
# Register your models here.


# class ProductInline(admin.TabularInline):
#     autocomplete_fields = ['title']
#     model = Product

@admin.register(LikedItem)
class LikedItemAdmin(admin.ModelAdmin):
    list_display = ['user']
    autocomplete_fields =['user']
    list_select_related = ['user']
    # inlines =[ProductInline]

