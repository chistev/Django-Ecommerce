from django.contrib import admin
from .models import Product, UserActivity, SuperCategory, Category


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('discount_percentage',)


admin.site.register(Product, ProductAdmin)
admin.site.register(UserActivity)
admin.site.register(SuperCategory)
admin.site.register(Category)
