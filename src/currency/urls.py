from django.urls import path

from currency import views


app_name = 'currency'

urlpatterns = [
    path('last-rates/', views.LastRates.as_view(), name='last-rates'),
    path('download/rates/', views.RateCSV.as_view(), name='download-rates'),
    path('latest-rates/', views.LatestRates.as_view(), name='latest-rates'),
    path('exchangers/', views.Exchangers.as_view(), name='exchangers'),

    path('comment-creation/<int:pk>', views.comment_creation, name='comment-creation'),
]
