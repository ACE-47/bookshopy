from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from . import models

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id','title','unit_price']


class authorSerializers(serializers.ModelSerializer):
    products = SimpleProductSerializer(many =True)
    class Meta:
        model = models.Author
        fields = ['id' ,'name', 'about', 'birth_date', 'products','author_image']


    def get_products(self,author:models.Author):
        return models.Product.objects.prefetch_related('products').filter(auther_id = author.pk)[:5]


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only = True)
    class Meta:
        model = models.Collection
        fields = ['id','title', 'products_count']

    

class ProductImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.ProductImage
        fields = ['id', 'image']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return models.ProductImage.objects.create(product_id = product_id, **validated_data)


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Publisher
        fields = ['id', 'name']


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Promotion
        fields = ['id', 'title', 'descriptions', 'discount',]

class SimpleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = ['id', 'name']

class ProdcutSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many = True, read_only = True)
    publisher = PublisherSerializer( read_only = True)
    auther = SimpleAuthorSerializer()
    promotion = PromotionSerializer()
   
    
    class Meta:
        model = models.Product
        fields = ['id','title','descriptions','slug', 'inventory','unit_price','collection','publisher','auther','images', 'promotion']

    # def get_auther(self, author:models.Author):
    #     return author.name & author.id
        # return 0
    


class ProductAdverSerializer(serializers.ModelSerializer):
    # consider this solution or make light version of product serializer 
    # product = SimpleAuthorSerializer()
    product = ProdcutSerializer()
    class Meta: 
        model = models.ProductAdvertize
        fields =['product']

# package
        
class PackageItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = models.PackageItem
        fields = ['id', 'package', 'product', 'quantity']
        
        
class PackageSerializer(serializers.ModelSerializer):
    items = PackageItemSerializer(many = True, read_only = True)
    class Meta:
        model = models.Package
        fields =['id', 'title','descriptions', 'items', 'unit_price', 'image']
        # fields =['id', 'title', 'unit_price']
        
    def create(self, validated_data):
        user = self.context['user']
        return models.Package.objects.create(created_by = user, **validated_data) 
    
    
class AddPackageItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    package_id = serializers.IntegerField(read_only = True)
    
    class Meta:
        model = models.PackageItem
        fields = ['id', 'package_id', 'product_id', 'quantity']
        
    def validate_product_id(self, value):
        if not models.Product.objects.filter(pk = value).exists():
            return serializers.ValidationError('No Product with the given ID was found!')
        return value
    
    def save(self, **kwargs):
        package_id = self.context['package_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        
        try:
            packageItem = models.PackageItem.objects.get(package_id = package_id, product_id = product_id)
            packageItem.quantity += quantity
            packageItem.save()
            self.instance = packageItem
            
        except models.PackageItem.DoesNotExist:
            packageItem = models.PackageItem.objects.create(package_id = package_id, **self.validated_data)
            self.instance = packageItem
            
        return self.instance
    
class UpdatePackageItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PackageItem
        fields = ['quantity']
    
    

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = models.CartItem
        fields = ['id','product','package_id','quantity','total_price']

    def get_total_price(self, cartItem:models.CartItem):
        item = cartItem.product
        if item is not None:
            total = cartItem.quantity * item.unit_price 
            if item.promotion is not None:
                discount = item.unit_price * Decimal((item.promotion.discount / 100))
                discount_amount = item.unit_price - discount
                return cartItem.quantity * discount_amount
            else:    
                return total
        return cartItem.quantity * cartItem.package.unit_price
        
class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only = True)
    items = CartItemSerializer(many = True, read_only = True)
    total_cart_price = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Cart
        fields = ['id','customer_id', 'items','total_cart_price']

    def get_total_cart_price(self, cart:models.Cart):
        # return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
        # total_cart_price = sum([(item.quantity * item.product.unit_price) if item.product is not None else (item.quantity * item.package.unit_price) for item in cart.items.all()])
        
        total_cart_price = Decimal(0.0)
        items = cart.items.all()
        for item in items:
            if item.product is not None:
                price = item.product.unit_price * item.quantity
                if item.product.promotion is not None:
                    discount_amount =  item.product.unit_price * Decimal(item.product.promotion.discount / 100)
                    total_cart_price += (item.product.unit_price - discount_amount) * item.quantity
                else:
                    total_cart_price += price
            else:
                total_cart_price += item.package.unit_price * Decimal(item.quantity)
            
        if cart.customer.promotion is not None:
            discount = cart.customer.promotion.discount
            discount_amount = total_cart_price * Decimal(discount / 100)
            return total_cart_price - discount_amount
        
        return total_cart_price
        
        # for item in cart.items.all():
        #     if item.product == None:
        #         return sum(item.quantity * item.package.unit_price)
        #     else:
        #         item.quantity * item.product.unit_price
            
    
    def save(self, **kwargs):
        user_id = self.context['user_id']
        customer = models.Customer.objects.get(user_id = user_id)
        
        
        if models.Cart.objects.filter(customer_id = customer.id).exists():
            raise serializers.ValidationError('Cart already Existis')
        
        # try:
        cart = models.Cart.objects.create(customer = customer)
        cart.save()
        self.instance = cart
        # except:
        
        return self.instance
        

class AddCartItemSerializer(serializers.ModelSerializer):
    package_id = serializers.IntegerField(required=False,allow_null=True,)
    product_id = serializers.IntegerField(required=False,allow_null=True,)
    class Meta:
        model = models.CartItem
        fields = ['id', 'product_id', 'package_id', 'quantity']
        # extra_kwargs = {'product_id': {'required': False},
        #                 'package_id': {'required': False}
        #                 } 

    def validate_product_id(self, value):
        if value != None:
            if not models.Product.objects.filter(pk = value).exists():
                raise serializers.ValidationError('No Product with the given ID was found!')    
        return value
    
    def validate_package_id(self, value):
        if value != None:
            if not models.Package.objects.filter(pk = value).exists():
                return serializers.ValidationError('No such package with the given ID')
        return value
    
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        package_id = self.validated_data['package_id']
        quantity = self.validated_data['quantity']

        try:
            if product_id != None and package_id == None:
                cartitem = models.CartItem.objects.get(cart_id = cart_id, product_id = product_id)
                cartitem.quantity += quantity
                cartitem.save()
            else:
                cartitem = models.CartItem.objects.get(cart_id = cart_id, package_id = package_id)
                cartitem.quantity += quantity
                cartitem.save()
            
            self.instance = cartitem
        except models.CartItem.DoesNotExist:
            cartitem = models.CartItem.objects.create(cart_id = cart_id, **self.validated_data)
            self.instance = cartitem
        
        return self.instance


        # return super().save(**kwargs)
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.CartItem
        fields = ['quantity']

# location

class AddressSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only = True)
    class Meta:
        model = models.Address
        fields = ['id','capital', 'city', 'street', 'more_info']
        
# Customer
       
class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    # address = AddressSerializer()
    
    class Meta:
        model =models.Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'address']
        
        
    # def update(self, instance, validated_data):
    #     address = validated_data['address']
    #     # address_id = validated_data['address']['id']
    #     print(validated_data)
    #     customer_id = instance.pk
        
    #     try:
    #         address = models.Address.objects.get(address_id = address.pk)
    #         customer = models.Customer.objects.update(customer_id = customer_id,**self.validated_data)
    #         customer.save()
    #         instance = customer
            
    #     except models.Address.DoesNotExist:
    #         address = models.Address.objects.create(**address)
    #         customer = models.Customer.objects.update(customer_id = customer_id, **self.validated_data)
    #         customer.save()
    #         instance = customer
            
    #     return instance
    
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()
    package = PackageSerializer()
    class Meta:
        model = models.OrderItem
        fields = ['product', 'quantity', 'package', 'total_price']

    def get_total_price(self, orderItem:models.OrderItem):
        if orderItem.product is not None:
            return orderItem.quantity * orderItem.unit_price
        return orderItem.quantity * orderItem.package.unit_price
# def get_total_cart_price(self, cart:models.Cart):
#         return sum([item.quantity * item.product.unit_price for item in cart.items.all()])



        
       

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many = True)
    # total_order_price = serializers.SerializerMethodField()
    address = AddressSerializer()
    class Meta:
        model = models.Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items','total_order_price', 'address']

    # def get_total_order_price(self, order:models.Order):
    #     return sum(item.quantity * item.unit_price for item in order.items.all())
        


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['payment_status']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    address = AddressSerializer()

    def validate_cart_id(self, cart_id):
        # print(cart_id)
        if not models.Cart.objects.filter(pk = cart_id).exists():
            raise serializers.ValidationError('No Cart with the given ID was Found')
        
        if models.CartItem.objects.filter(cart_id = cart_id).count() == 0:
            raise serializers.ValidationError('the current Cart is Empty')
        
        return cart_id

    
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user = self.context['user']
            address = self.validated_data['address']
            
            customer = models.Customer.objects.get(user_id = user.id)
            address = models.Address.objects.create(user = user ,**self.validated_data['address'])
            order = models.Order.objects.create(customer = customer, address = address)

            cartItems = models.CartItem.objects.select_related('product').filter(cart_id = cart_id)

            orderItems = [
                models.OrderItem(
                            order = order,
                            product = item.product,
                            package = item.package,
                            unit_price = item.product.unit_price - (item.product.unit_price * (item.product.promotion / 100)) if item.product.promotion is not None else item.product.unit_price if item.product is not None else item.package.unit_price,
                            quantity = item.quantity,
                            ) for item in cartItems ]
            
            
            total_order_price = sum(item.quantity * item.unit_price for item in orderItems)
            if customer.promotion is not None:
                discount = customer.promotion.discount / 100
                discount_amount = total_order_price * discount
                total_order_price -= discount_amount
                order.objects.update(total_order_price = total_order_price, **order)
                customer.objects.update(promotion = None)
            # print(orderItems)
            models.OrderItem.objects.bulk_create(orderItems)
            
            models.Cart.objects.filter(pk = cart_id).delete()
            return order
