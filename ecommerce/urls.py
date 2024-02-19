from django.urls import path
from . import views


app_name = 'ecommerce'

urlpatterns = [
    path('', views.index, name='index'),
    path('supermarket/', views.supermarket, name='supermarket'),
]
