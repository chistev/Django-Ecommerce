from django.urls import path
from . import views
from .views import CustomLogoutView

app_name = 'accounts'

urlpatterns = [
    path('login_or_register/', views.login_or_register, name='login_or_register'),
    path('login/<str:email>/', views.login, name='login'),
    path('register/<str:email>/', views.register, name='register'),
    path('personal_details/', views.personal_details, name='personal_details'),
    path('successful_registration/', views.successful_registration, name='successful_registration'),
    path('terms_and_conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('sign_out/', CustomLogoutView.as_view(), name='sign_out'),
    path('my_account/', views.my_account, name='my_account'),
    path('orders/', views.orders, name='orders'),
    path('closed_orders/', views.closed_orders, name='closed_orders'),
    path('inbox/', views.inbox, name='inbox'),
    path('saved_items/', views.saved_items, name='saved_items'),
    path('account_management/', views.account_management, name='account_management'),
]
