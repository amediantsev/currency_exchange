from django.urls import path

from account import views


app_name = 'account'

urlpatterns = [
    path('signup/index/', views.SignUpIndex.as_view(), name='signup-index'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('signup/sms/', views.SignUpSMS.as_view(), name='signup-sms'),

    path('profile/<int:pk>/', views.MyProfile.as_view(), name='my-profile'),
    path('contact-us/', views.ContactUs.as_view(), name='contact-us'),

    path('activate/<uuid:activation_code>', views.Activate.as_view(), name='activate'),
    path('sms-activate/', views.SMSActivate.as_view(), name='sms-activate'),
]
