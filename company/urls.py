from django.urls import path, include
from rest_framework import routers
from .views import *
from . import json

router = routers.DefaultRouter()
router.register(r'staff', CompanyStaffViewSet, basename='staff')
router.register(r'chatbox', AppChatRoomViewSet, basename='chatbox')
router.register(r'message', ChatMessageViewSet, basename='message')
router.register(r'accounts', CompanyAccountsViewSet, basename='accounts')
router.register(r'customers', CompanyCustomerViewSet, basename='customers')
router.register(r'departments', CompanyDepartmentViewSet, basename='departments')
router.register(r'positions', CompanyPossitionViewSet, basename='positions')
router.register(r'vendors', CompanyVendorViewSet, basename='vendors')
router.register(r'ops', CompanyOperatorViewSet, basename='ops')
router.register(r'approvehis', AdvanceRequestHistoryViewSet, basename='approvehis')
router.register(r'ophist', OperatorWorkHistoryViewSet, basename='ophist')
router.register(r'profile', CompanyStaffProfileViewSet, basename='profile')
router.register(r'info', CompanyStaffProfileViewSet, basename='info')
router.register(r'approve', AdvanceRequestViewSet, basename='approve')
router.register(r'approvel', AdvanceRequestLTEViewSet, basename='approvel')
router.register(r'approveX', AdvanceRequestExportViewSet, basename='approveX')
router.register(r'com', CompanyViewSet, basename='com')
router.register(r'op_all', CompanyOperatorAllDetailsViewSet, basename='op_all')
urlpatterns = [
    path('op/add/', AddOperatorAPIView.as_view(), name='add-op'),
    path('search/', SearchAPIView.as_view(), name='search'),
    path('login/', LoginOAuth2APIView.as_view(), name='login'),
    path('user/', GetUserAPIView.as_view(), name='user'),
    path('user_socket/', GetUserSocketAPIView.as_view(), name='user_socket'),
    path('banks/', json.banks, name='banks'),
    path('', include(router.urls)),
]
# 48MghDAMhSXJoPZKwQ7BZoRVIjQJLowv7QFrtT08
# TQJz3zEIa8AKYbjQ3xDdm5UNxFnhUJC2s08UPhgznsfzaiAfeIx6BGGCD
# ADTlAWse8xc3DqCoGsfNjIsAdhTRWWeZtxlLDYW0kwXYHEeZYQaLzKnwXeFZWcWlpg6DBwU