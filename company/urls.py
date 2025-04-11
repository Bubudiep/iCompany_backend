from django.urls import path, include
from rest_framework import routers
from .views import *
from . import json

router = routers.DefaultRouter()
router.register(r'staff', CompanyStaffViewSet, basename='staff')
router.register(r'chatbox', AppChatRoomViewSet, basename='chatbox')
router.register(r'accounts', CompanyAccountsViewSet, basename='accounts')
urlpatterns = [
    path('search/', SearchAPIView.as_view(), name='search'),
    path('login/', LoginOAuth2APIView.as_view(), name='login'),
    path('user/', GetUserAPIView.as_view(), name='user'),
    path('user_socket/', GetUserSocketAPIView.as_view(), name='user_socket'),
    path('banks/', json.banks, name='banks'),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('', include(router.urls)),
]
# 48MghDAMhSXJoPZKwQ7BZoRVIjQJLowv7QFrtT08
# TQJz3zEIa8AKYbjQ3xDdm5UNxFnhUJC2s08UPhgznsfzaiAfeIx6BGGCD
# ADTlAWse8xc3DqCoGsfNjIsAdhTRWWeZtxlLDYW0kwXYHEeZYQaLzKnwXeFZWcWlpg6DBwU