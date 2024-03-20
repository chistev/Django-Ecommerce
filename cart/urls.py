from django.urls import path

from . import views
from .views import cart_view

app_name = 'cart'

urlpatterns = [
    path('cart/', cart_view, name='cart'),
    path('remove_all_from_cart/', views.remove_all_from_cart, name='remove_all_from_cart'),
]
