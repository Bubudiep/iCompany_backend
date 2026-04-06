from django.urls import path, include
from rest_framework import routers
from .views import *
router = routers.DefaultRouter()
router.register(r'ehs', EHSIssueViewSet, basename='ehs')
router.register(r'my-ehs', MyEHSIssueViewSet, basename='my_ehs')
router.register(r'mail', MailRequestViewSet, basename='mail_requests')
router.register(r'qna', QNARequestViewSet, basename='qna_requests')
router.register(r'notifications', ZUserNotificationViewSet, basename='notifications')
urlpatterns = [
    path('auth/login/', ZaloMemberLogin.as_view(), name='auth_login'),
    path("", include(router.urls)),
]