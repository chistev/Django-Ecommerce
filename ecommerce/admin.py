from django.contrib import admin
from .models import Product, UserActivity


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('discount_percentage',)


admin.site.register(Product, ProductAdmin)
admin.site.register(UserActivity)
