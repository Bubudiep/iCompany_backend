from django.urls import path, include
from rest_framework import routers
from .views import *
router = routers.DefaultRouter()
router.register(r'ehs', EHSIssueViewSet, basename='ehs')
urlpatterns = [
    path('auth/login/', ZaloMemberLogin.as_view(), name='auth_login'),
]