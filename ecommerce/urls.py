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
    path('air_conditioner/', views.air_conditioner, name='air_conditioner'),
    path('fan/', views.fan, name='fan'),
    path('freezer/', views.freezer, name='freezer'),
    path('microwave/', views.microwave, name='microwave'),
    path('fridge/', views.fridge, name='fridge'),
    path('washing_machine/', views.washing_machine, name='washing_machine'),
    path('android_phones/', views.android_phones, name='android_phones'),
    path('iphones/', views.iphones, name='iphones'),
    path('accessories/', views.accessories, name='accessories'),
    path('cellphones/', views.cellphones, name='cellphones'),
    path('laptops/', views.laptops, name='laptops'),
    path('flash_drive/', views.flash_drive, name='flash_drive'),
    path('hard_drive/', views.hard_drive, name='hard_drive'),
    path('printers/', views.printers, name='printers'),
    path('ps4/', views.ps4, name='ps4'),
    path('controllers/', views.controllers, name='controllers'),
    path('ps5/', views.ps5, name='ps5'),
    path('xbox/', views.xbox, name='xbox'),
    path('api/products/', views.filter_products, name='filter_products'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/count/', views.cart_count, name='cart_count'),
    path('return_policy', views.return_policy, name='return_policy'),
    path('save_product', views.save_product, name='save_product'),
    path('search/', views.product_search, name='product_search'),
    path('autocomplete/', autocomplete, name='autocomplete'),
]
