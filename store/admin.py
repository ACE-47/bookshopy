from typing import Any, List, Optional, Tuple
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse

from . import models

# Register your models here.

class InventoryFilter(admin.SimpleListFilter):
    title = 'Inventory'
    parameter_name = 'inventory'

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        return [
            ('<10','LOW'),
        ]
    
    def queryset(self, request: Any, queryset: QuerySet) :
        if self.value() == '<10':
            return queryset.filter(inventory__lt = 10)
        
class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instanc : models.ProductImage):
        return format_html(f'<img src="{instanc.image.url}" class="thumbnail"/>')

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ['clear_inventory']
    inlines = [ProductImageInline]
    search_fields =['title']
    autocomplete_fields = ['collection']
    prepopulated_fields = {'slug':['title']}
    list_display = ['title', 'unit_price', 'collection', 'inventory_status', 'inventory']
    list_filter = ['collection','last_update', InventoryFilter]

    list_per_page = 20

    @admin.display(ordering='inventory')
    def inventory_status(self, product:models.Product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request,queryset:QuerySet):
        updated_count = queryset.update(inventory = 0)
        self.message_user(
            request,
            f'{updated_count} was seccessfuly updated '
        )

    class Media:
        css = {
            'all':['store/styles.css']
        }

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['title','products_count']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (reverse('admin:store_product_changelist') + '?' + urlencode({'collection_id':str(collection.id)}))
        return format_html('<a href={}>{}<a>',url,collection.products_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count = Count('products'))
    

class CustomerAdmin(admin.ModelAdmin):
    