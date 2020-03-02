from django.contrib import admin
from django.urls import path, include

import django.contrib.auth.urls
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),

    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('account/', include('account.urls')),
]
