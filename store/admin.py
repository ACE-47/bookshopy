from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields =['title']
    # autocomplete_fields = ['collection']
    prepopulated_fields = {'slug':['title']}
    list_display = ['title', 'unit_price', 'collection', 'inventory']
    list_per_page = 10

