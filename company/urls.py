from django.urls import path, include
from rest_framework import routers
from .views import *
from . import json

router = routers.DefaultRouter()
urlpatterns = [
    path('login/', LoginOAuth2APIView.as_view(), name='login'),
    path('user/', GetUserAPIView.as_view(), name='user'),
    path('banks/', json.banks, name='banks'),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('', include(router.urls)),
]
# 48MghDAMhSXJoPZKwQ7BZoRVIjQJLowv7QFrtT08
# TQJz3zEIa8AKYbjQ3xDdm5UNxFnhUJC2s08UPhgznsfzaiAfeIx6BGGCDADTlAWse8xc3DqCoGsfNjIsAdhTRWWeZtxlLDYW0kwXYHEeZYQaLzKnwXeFZWcWlpg6DBwU