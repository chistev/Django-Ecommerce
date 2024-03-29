from django.urls import path
from .views import checkout_view, order_success_view

app_name = 'checkout'

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('order_success/', order_success_view, name='order_success'),
]
