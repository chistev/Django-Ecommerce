from django.urls import path
from . import views
from .views import CustomLogoutView

app_name = 'accounts'

urlpatterns = [
    path('login_or_register/', views.login_or_register, name='login_or_register'),
    path('register/<str:email>/', views.register, name='register'),
    path('personal_details/', views.personal_details, name='personal_details'),
    path('successful_registration/<str:first_name>/', views.successful_registration, name='successful_registration'),
    path('login/<str:email>/', views.login, name='login'),
    path('terms_and_conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('sign_out/', CustomLogoutView.as_view(), name='sign_out'),
    path('my_account/', views.my_account, name='my_account'),
    path('orders/', views.orders, name='orders'),
    path('order_details/<str:order_number>/', views.order_details, name='order_details'),
    path('order/<str:order_number>/cancel/', views.cancel_order, name='cancel_order'),
    path('closed_orders/', views.closed_orders, name='closed_orders'),
    path('inbox/', views.inbox, name='inbox'),
    path('saved_items/', views.saved_items, name='saved_items'),
    path('account_management/', views.account_management, name='account_management'),
    path('basic_details/', views.basic_details, name='basic_details'),
    path('edit_basic_details/', views.edit_basic_details, name='edit_basic_details'),
    path('change_password/', views.change_password, name='change_password'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('address_book/', views.address_book, name='address_book'),
    path('address_book_create/', views.address_book_create, name='address_book_create'),
    path('address_book_edit/<int:address_id>/', views.address_book_edit, name='address_book_edit'),
    path('get_cities/', views.get_cities, name='get_cities'),
    path('remove_saved_product/', views.remove_saved_product, name='remove_saved_product'),
    path('forgot_password/<str:email>/', views.forgot_password, name='forgot_password'),
    path('security_code_reset', views.security_code_reset, name='security_code_reset'),
    path('resend_security_code/', views.resend_security_code, name='resend_security_code'),
    path('password_reset/', views.password_reset, name='password_reset'),
]
