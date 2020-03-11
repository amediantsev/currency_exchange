from django.urls import path

from currency import views


app_name = 'currency'

urlpatterns = [
    path('last-rates/', views.LastRates.as_view(), name='last-rates'),
]
