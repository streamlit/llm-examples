from django.urls import include, path
from django.contrib import admin
from django.shortcuts import redirect
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('app/', include('frontend.urls')),
    path('', lambda request: redirect('accounts/')),
    path('api/', include('api.urls')),
]
