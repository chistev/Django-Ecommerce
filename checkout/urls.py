from django.urls import path
from .views import checkout_view, order_success_view, payment_method_view, flutterwave_payment_view, \
    transfer_success_view, flutterwave_webhook_view

app_name = 'checkout'

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('order_success/', order_success_view, name='order_success'),
    path('transfer_success/', transfer_success_view, name='transfer_success'),
    path('payment_method/', payment_method_view, name='payment_method'),
    path('flutterwave_payment/', flutterwave_payment_view, name='flutterwave_payment'),
    path('flutterwave_webhook/', flutterwave_webhook_view, name='flutterwave_webhook'),
]
