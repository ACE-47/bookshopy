from typing import Any, List, Optional, Tuple
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse

from . import models

# Register your models here.

# class AuthorImageInline(admin.TabularInline):
#     model = models.Author
#     readonly_fields = ['thumbnail']

#     def thumbnail(self, instanc : models.Author):
#         return format_html(f'<img src="{instanc.image.url}" class="thumbnail"/>')
    

@admin.register(models.Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title','discount', 'description']



@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):

    list_display = ['name', 'about', 'birth_date','products_count']
    readonly_fields = ['image_tag']
    search_fields =['name']

    list_per_page = 10

    def image_tag(self, author:models.Author):
        if author.author_image.url is not None:
            return format_html(f'<img src="{author.author_image.url}" class="thumbnail"/>')
        
    image_tag.short_description = 'Image'
    
        

    @admin.display(ordering='products_count')
    def products_count(self, author:models.Author):
        url = (reverse('admin:store_product_changelist') + '?' 
               + urlencode({'auther_id':str(author.id)}))
        return format_html('<a href={}>{}<a>',url,author.products_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count = Count('products'))
   
    class Media:
        css = {
            'all':['store/styles.css']
        }
        
@admin.register(models.Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'descriptions', 'products_count']
    search_fields = ['name']
    list_per_page = 10

    @admin.display(ordering='products_count')
    def products_count(self, publisher:models.Publisher):
        url = (reverse('admin:store_product_changelist') + '?' 
               + urlencode({'publisher_id':str(publisher.id)}))
        return format_html('<a href={}>{}<a>',url,publisher.products_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count = Count('products'))


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
    list_display = ['title', 'unit_price', 'collection', 'inventory_status', 'inventory',]
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
    def products_count(self, collection:models.Collection):
        url = (reverse('admin:store_product_changelist') + '?' 
               + urlencode({'collection_id':str(collection.id)}))
        return format_html('<a href={}>{}<a>',url,collection.products_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count = Count('products'))
    
# 
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name','orders']
    list_per_page = 20
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']

    autocomplete_fields = ['user']

    @admin.display(ordering='orders')
    def orders(self, customer):
        url = (reverse('admin:store_order_changelist') + 
               '?'
                + urlencode({'customer_id':str(customer.id)}))
        return format_html('<a href={}>{}</a>',url, customer.orders)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(orders = Count('order'))
    

class OrderItemInline(admin.TabularInline):
    model =  models.OrderItem
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    extra = 0

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    autocomplete_fields = ['customer']
    list_display = ['id', 'customer','placed_at', 'payment_status',]
    ordering = ['-placed_at']
    list_editable = ['payment_status']
    list_per_page = 20
