from django.db import models


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
