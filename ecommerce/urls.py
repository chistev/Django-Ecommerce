from django.urls import path
from . import views


app_name = 'ecommerce'

urlpatterns = [
    path('', views.index, name='index'),
    path('supermarket/', views.supermarket, name='supermarket'),
    path('grains_and_rice/', views.grains_and_rice, name='grains_and_rice'),
    path('food_cupboard/', views.food_cupboard, name='food_cupboard'),
    path('household_care/', views.household_care, name='household_care'),
    path('laundry/', views.laundry, name='laundry'),
    path('fragrances/', views.fragrances, name='fragrances'),
    path('api/products/', views.filter_products, name='filter_products'),
]
