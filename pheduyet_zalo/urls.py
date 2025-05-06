from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'group', UserGroupViewSet, basename='group')
router.register(r'profile', ZaloUserProfileViewSet, basename='profile')
urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('user/', GetUserAPIView.as_view(), name='user'),
    path('', include(router.urls)),
]