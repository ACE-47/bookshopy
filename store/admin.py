from typing import Any, List, Optional, Tuple
from django import forms
from django.shortcuts import redirect
from django.urls.resolvers import URLPattern
from django.utils.safestring import mark_safe 
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import path, reverse
from django.core.validators import MinValueValidator

from . import models

# Register your models here.

# class AuthorImageInline(admin.TabularInline):
#     model = models.Author
#     readonly_fields = ['thumbnail']

#     def thumbnail(self, instanc : models.Author):
#         return format_html(f'<img src="{instanc.image.url}" class="thumbnail"/>')
    

@admin.register(models.Promotion)
class PromotionAdmin(admin.ModelAdmin):
    
    list_display = ['id', 'title','discount', 'descriptions']



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
    list_display = ['id', 'title', 'unit_price', 'collection', 'inventory_status', 'inventory','last_update']
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


@admin.register(models.ProductAdvertize)
class ProductAdvertizeAdmin(admin.ModelAdmin):
    autocomplete_fields = ['product']
    list_display = ['product' , 'product_id']

    def product_id(self, productAd:models.ProductAdvertize):
        url = (reverse('admin:store_product_changelist') + 
               str(productAd.product.id)
            #    + '?' 
            #    + urlencode({'':str(productAd.id)})
               )
        return format_html('<a href={}>{}<a>',url,productAd.product.id)

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['featured_product']
    search_fields = ['title']
    list_display = ['title','products_count']


    @admin.display(ordering='products_count')
    def products_count(self, collection:models.Collection):
        url = (reverse('admin:store_product_changelist') + '?' 
               + urlencode({'collection_id':str(collection.id)}))
        return format_html('<a href={}>{}<a>',url,collection.products_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count = Count('products'))
    

# action for customer and promotion
# form for promotion 

class PromotionSelectionForm(forms.Form):
    promotion = forms.ModelChoiceField(queryset=models.Promotion.objects.all(), required=False)
    title = forms.CharField(max_length=255, required=False)
    # discount = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    discount = forms.IntegerField( validators = [MinValueValidator(0)], required = False)
    descriptions = forms.CharField(required = False)


# 
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    # action_form = assign_promotion()
    actions = ['assign_promotion']
    list_display = ['first_name', 'last_name', 'phone', 'birth_date','orders','cart_id', 'discount','address']
    list_per_page = 20
    list_select_related = ['user', 'promotion', 'address']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']

    autocomplete_fields = ['user']
    
    # def address(self, customer:models.Customer):
    #     return customer.location.capital
    
    def discount(self, customer:models.Customer):
        if customer.promotion is not None:
            return customer.promotion.discount
        return 0
    
    def cart_id(self, customer):
        url = (reverse('admin:store_cart_change', args=(customer.cart.id,)) )
        return format_html('<a href={}>{}</a>',url, customer.cart.id)
        # return customer.cart.id

    @admin.display(ordering='orders')
    def orders(self, customer):
        url = (reverse('admin:store_order_changelist') + 
               '?'
                + urlencode({'customer_id':str(customer.id)}))
        return format_html('<a href={}>{}</a>',url, customer.orders)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(orders = Count('order'))
    

    @admin.action(description = 'assign promotion')
    def assign_promotion(self, request, queryset:QuerySet):
        if 'apply' in request.POST:
            form = PromotionSelectionForm(request.POST)
            if form.is_valid():
                promotion = form.cleaned_data['promotion']
                title = form.cleaned_data['title']
                discount = form.cleaned_data['discount']
                descriptions = form.cleaned_data['descriptions']
                
            if not promotion and title and discount and descriptions:
                promotion = models.Promotion.objects.create(title = title, descriptions = descriptions, discount = discount)
                queryset.update(promotion = promotion)
                self.message_user(request, f"Promotion '{promotion}' has been assigned to the selected customers.")
                return redirect(request.get_full_path())
        else:
            form = PromotionSelectionForm()
    
    
    def get_urls(self) -> List[URLPattern]:
        urls =  super().get_urls()
        custom_url = [
            path('assign_promotion/',self.admin_site.admin_view(self.assign_promotion), name = 'assign_promotion' )
        ]
        return custom_url + urls
        
        
        
# package 
class PackageItemInline(admin.TabularInline):
    model = models.PackageItem
    autocomplete_fields = ['product']
    
    
    

@admin.register(models.Package)
class PackageAdmin(admin.ModelAdmin):
    inlines = [PackageItemInline]
    list_display = ['id', 'title', 'descriptions', 'unit_price', 'created_by', 'created_at']
    list_per_page = 10
    list_select_related = ['created_by']
    autocomplete_fields = ['created_by']
    ordering = ['created_at', 'title']
    


# @admin.register(models.CartItem)
class CartItemInline(admin.TabularInline):
    model = models.CartItem
    autocomplete_fields = ['product']
    extra = 1
    

@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ['id', 'customer', 'created_at']
    autocomplete_fields = ['customer']
    
    
    # @admin.display()
    # def customer_name(self, customer:models.Customer):
    #     url = (reverse('admin:store_customer_changelist') + '?' 
    #            + urlencode({'customer_id':str(customer.id)}))
    #     return format_html('<a href={}>{}<a>',url,customer.customer)


# Address Admin

@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    model = models.Address
    search_fields = ['city']
    # autocomplete_fields = ['city']
    list_display = ['id', 'user', 'capital','city', 'street']

class OrderItemInline(admin.TabularInline):
    model =  models.OrderItem
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    extra = 0

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    autocomplete_fields = ['customer', 'address']
    # list_display = ['id', 'customer', 'placed_at', 'payment_status',]
    list_display = ['id', 'customer', 'total_order_price','placed_at', 'payment_status', 'address_id']
    ordering = ['-placed_at']
    list_editable = ['payment_status']
    list_per_page = 20

    def address_id(self, order):
        url = (reverse('admin:store_address_change', args=(order.address.id,)) )
        return format_html('<a href={}>{}</a>',url, order.address.id)
    
# admin:auth_user_change
    
    # @admin.display(ordering='orders')
    # def total_price(self, order:models.Order):
    #     print(order.items.all())
    #     return sum([item.unit_price * item.quantity for item in order.items.all()])
    
    # def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        
    #     return super().get_queryset(request).annotate(total_price = Count('items'))

# 