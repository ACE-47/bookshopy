from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.validators import MinValueValidator

from .validatiors import validate_file_size 
# Create your models here.

class Publisher(models.Model):
    name = models.CharField(max_length=255)
    descriptions = models.TextField(null=True, blank=True)
  

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='+') # the + tell django to not created reverse field in Product model

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        ordering = ['title']

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()

class Author(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    author_image = models.ImageField(upload_to='store/author_images',blank=True, null=True) # set default image 

    def __str__(self):
        return self.name




class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    descriptions = models.TextField()
    # change decimail settings based on DIQ
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators= [MinValueValidator(1)]
        ) #9999.99  
    
    pages = models.IntegerField(null=True, blank=True)
    
    inventory = models.IntegerField(validators= [MinValueValidator(0)], default=1)
    last_update = models.DateTimeField(auto_now=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name='products')
    promotions = models.ManyToManyField(Promotion,blank=True)
    auther = models.ForeignKey(Author, on_delete=models.PROTECT, related_name='products')

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']


class ProductImage(models.Model):

# if its FileField you can validate the extenstion of file such as .pdf 
# file = models.FileField(upload_to='store/images', validators=[FileExtensionValidator(allow_extensions =['pdf])])

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='store/images', )


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)

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


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING,'Pending'),
        (PAYMENT_STATUS_COMPLETE,'Complete'),
        (PAYMENT_STATUS_FAILED,'Failed'),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        permissions = [('cancel_order', 'Can cancel order')]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6,decimal_places =2 )


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [['cart', 'product']]


class Adress(models.Model):
    street =models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    # zip = models.CharField(max_length=255)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

# class Review(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')

#     # forignKey with User model (replaced with) note
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     date = models.DateField(auto_now_add=True)

