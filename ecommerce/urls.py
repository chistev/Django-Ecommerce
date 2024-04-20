from django.urls import path, re_path
from . import views
from .views import autocomplete

app_name = 'ecommerce'

urlpatterns = [
    path('', views.index, name='index'),
    path('supermarket/', views.supermarket, name='supermarket'),
    re_path(r'^category/(?P<category_name>[\w\s&-]+)/$', views.category_products, name='category'),
    path('home_and_office/', views.home_and_office, name='home_and_office'),
    path('phones_and_accessories/', views.phones_and_accessories, name='phones_and_accessories'),
    path('computing/', views.computing, name='computing'),
    path('gaming/', views.gaming, name='gaming'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/count/', views.cart_count, name='cart_count'),
    path('return_policy', views.return_policy, name='return_policy'),
    path('save_product', views.save_product, name='save_product'),
    path('search/', views.product_search, name='product_search'),
    path('autocomplete/', autocomplete, name='autocomplete'),
]
