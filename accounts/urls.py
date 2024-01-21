from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login_or_register/', views.login_or_register, name='login_or_register'),
    path('login/<str:email>/', views.login, name='login'),
    path('register/<str:email>/', views.register, name='register'),
    path('personal_details/', views.personal_details, name='personal_details'),
    path('successful_registration/', views.successful_registration, name='successful_registration'),
    path('terms_and_conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('my-account/', views.my_account, name='my-account'),
    path('orders/', views.orders, name='orders'),
    path('saved-items/', views.saved_items, name='saved-items'),
]
