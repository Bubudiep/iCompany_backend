from django.urls import path
from .views import SearchKaraokeAPI, GetStreamUrlAPI

urlpatterns = [
    path('search/', SearchKaraokeAPI.as_view(), name='ktube-search'),
    path('stream/', GetStreamUrlAPI.as_view(), name='ktube-stream'),
]