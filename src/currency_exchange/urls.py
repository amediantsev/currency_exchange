from django.contrib import admin
from django.urls import path, include

import django.contrib.auth.urls
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),

    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    path('account/', include('account.urls')),
    path('currency/', include('currency.urls')),

    # API
    path('api/v1/currency/', include('currency.api.urls')),
]

from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='DOCS')

urlpatterns.append(path(rf'api/v1/docs/', schema_view))

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
