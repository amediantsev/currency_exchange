from django.urls import path

from account import views


app_name = 'account'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
]
