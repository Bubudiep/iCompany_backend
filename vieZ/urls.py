from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'user-files', UserFileViewSet, basename='userfile')
urlpatterns = [
    path('me/', MyInfo.as_view(), name='me'),
    path('login/', Login.as_view(), name='login'),
    path('', include(router.urls)),
]
# 48MghDAMhSXJoPZKwQ7BZoRVIjQJLowv7QFrtT08
# TQJz3zEIa8AKYbjQ3xDdm5UNxFnhUJC2s08UPhgznsfzaiAfeIx6BGGCD
# ADTlAWse8xc3DqCoGsfNjIsAdhTRWWeZtxlLDYW0kwXYHEeZYQaLzKnwXeFZWcWlpg6DBwU