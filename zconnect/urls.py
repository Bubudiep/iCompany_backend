from django.urls import path, include
from rest_framework import routers
from .views import *
router = routers.DefaultRouter()
# router.register(r'profile', UserProfileViewSet, basename='userprofile')
urlpatterns = [
    path('auth/login/', ZaloMemberLogin.as_view(), name='auth_login'),
]