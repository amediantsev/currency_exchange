from django.urls import path

from account import views


app_name = 'account'

urlpatterns = [
    path('signup/', views.SignUp.as_view(template_name='signup.html'), name='signup'),
    path('profile/<int:pk>/', views.MyProfile.as_view(), name='my-profile'),
    path('contact-us/', views.ContactUs.as_view(), name='contact-us'),
    path('activate/<uuid:activation_code>', views.Activate.as_view(), name='activate'),
]
