from django.urls import path
from . import views


app_name = 'ecommerce'

urlpatterns = [
    path('', views.index, name='index'),
    path('supermarket/', views.supermarket, name='supermarket'),
    path('home_and_office/', views.home_and_office, name='home_and_office'),
    path('phones_and_tablets/', views.phones_and_tablets, name='phones_and_tablets'),
    path('grains_and_rice/', views.grains_and_rice, name='grains_and_rice'),
    path('food_cupboard/', views.food_cupboard, name='food_cupboard'),
    path('household_care/', views.household_care, name='household_care'),
    path('laundry/', views.laundry, name='laundry'),
    path('fragrances/', views.fragrances, name='fragrances'),
    path('air_conditioner/', views.air_conditoner, name='air_conditioner'),
    path('fan/', views.fan, name='fan'),
    path('freezer/', views.freezer, name='freezer'),
    path('microwave/', views.microwave, name='microwave'),
    path('fridge/', views.fridge, name='fridge'),
    path('washing_machine/', views.washing_machine, name='washing_machine'),
    path('android_phones/', views.android_phones, name='android_phones'),
    path('iphones/', views.iphones, name='iphones'),
    path('accessories/', views.accessories, name='accessories'),
    path('cellphones/', views.cellphones, name='cellphones'),
    path('api/products/', views.filter_products, name='filter_products'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/count/', views.cart_count, name='cart_count'),
    path('return_policy', views.return_policy, name='return_policy'),
    path('save_product', views.save_product, name='save_product'),

]
