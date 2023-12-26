from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ecommerce.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
]
urlpatterns += staticfiles_urlpatterns()
