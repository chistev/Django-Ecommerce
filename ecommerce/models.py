from django.db import models
from django.utils import timezone
from django.conf import settings



class Product(models.Model):
    CATEGORY_CHOICES = [
        ('grains_rice', 'Grains & Rice'),
        ('food_cupboard', 'Food Cupboard'),
        ('household_care', 'Household Care'),
        ('laundry', 'Laundry'),
        ('fragrances', 'Fragrances'),
        ('air_conditioner', 'Air Conditioner'),
        # Add more categories as needed
    ]
    name = models.CharField(max_length=100)
    image = models.ImageField()
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="None")

    def __str__(self):
        return self.name


class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    saved = models.BooleanField(default=False)  # a boolean field to track whether the product is saved by the user

    class Meta:
        ordering = ['-timestamp']


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='CartItem')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=10)


class Order(models.Model):
    order_number = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField('Product', through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)
    cancellation_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order {self.order.order_number}"


class PaymentEvent(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20)  # Status of the payment event (e.g., success, failed)

    def __str__(self):
        return f"PaymentEvent: {self.transaction_id}"
