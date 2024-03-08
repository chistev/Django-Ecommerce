from django.db import models
from django.utils import timezone
from django.conf import settings


class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField()
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    description = models.TextField()

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
