from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'files', UserFileViewSet, basename='userfiles')
router.register(r'apps', UserAppsViewSet, basename='userapps')
urlpatterns = [
    path('me/', MyInfo.as_view(), name='me'),
    path('login/', Login.as_view(), name='login'),
    path('zlogin/', ZaloMemberLogin.as_view(), name='zlogin'),
    path('', include(router.urls)),
]
# 48MghDAMhSXJoPZKwQ7BZoRVIjQJLowv7QFrtT08
# TQJz3zEIa8AKYbjQ3xDdm5UNxFnhUJC2s08UPhgznsfzaiAfeIx6BGGCD
# ADTlAWse8xc3DqCoGsfNjIsAdhTRWWeZtxlLDYW0kwXYHEeZYQaLzKnwXeFZWcWlpg6DBwU