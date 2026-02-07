import sys
import os
from django.conf import settings
from ..models import *
from ..serializers import *
from ..filters import *
from datetime import timedelta, datetime
from rest_framework import status
from oauthlib.common import generate_token
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.models import AccessToken, Application, RefreshToken
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from django.db import transaction
from django.utils.crypto import get_random_string
import pandas as pd
from rest_framework.parsers import MultiPartParser
from io import BytesIO
from django.http import HttpResponse
from django.db.models import Count
from django.utils.dateparse import parse_datetime

def generate_response_json(result:str, message:str, data:dict={}):
    return {"result": result, "message": message, "data": data}
  
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # Số lượng đối tượng trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 90000  # Số lượng đối tượng tối đa trên mỗi trang

def update_lastcheck(self, function_name="Accounts"):
    user = self.request.user
    key = self.request.headers.get('ApplicationKey')
    try:
        qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
    except CompanyStaff.DoesNotExist:
        raise exceptions.PermissionDenied("Không tìm thấy nhân sự tương ứng")
    LastCheckAPI.objects.update_or_create(
        function_name=function_name,
        user=qs_staff,
        defaults={'last_read_at': now}
    )
    return qs_staff

def check_permission(user_a, permission_name, permission_action):
    """
    Kiểm tra xem user_a có quyền cụ thể không.
    
    Args:
        user_a (User): Người dùng cần kiểm tra quyền.
        permission_name (str): Tên quyền cần kiểm tra.
    
    Returns:
        bool: True nếu có quyền, False nếu không.
    """
    try:
        # Lấy thông tin nhân viên từ tài khoản người dùng
        staff = CompanyStaff.objects.get(user__user=user_a)
        # Lấy tất cả các quyền của công ty liên quan đến nhân viên (bao gồm trực tiếp, bộ phận, chức vụ)
        applicable_permissions = CompanyPermission.objects.filter(
            Q(applicable_staff=staff) |
            Q(applicable_departments=staff.department) |
            Q(applicable_positions=staff.possition),
            is_active=True,
            permission__name=permission_name,
            permission_types__name=permission_action,
            company=staff.company
        ).exclude(excluded_staff=staff)  # Loại trừ nếu nhân viên nằm trong danh sách bị loại trừ
        # Nếu có ít nhất một quyền phù hợp
        if applicable_permissions.exists():
            return True
        return False
    except CompanyStaff.DoesNotExist:
        # Nhân viên không tồn tại
        return False
    
def generate_response_json(result:str, message:str, data:dict={}):
    return {"result": result, "message": message, "data": data}
def record_user_action(function_name,
                       action_name, staff, old_data=None, 
                       new_data=None, title=None, 
                       message=None, is_hidden=False, 
                       is_sended=False, is_received=False, is_readed=False,
                       ip_action=None):
    function = CompanyStaffHistoryFunction.objects.get_or_create(name=function_name)[0]
    action = CompanyStaffHistoryAction.objects.get_or_create(name=action_name)[0]
    history = CompanyStaffHistory.objects.create(
        ip_action=ip_action,
        staff=staff,
        function=function,
        action=action,
        old_data=old_data,
        new_data=new_data,
        title=title,
        message=message,
        isHidden=is_hidden,
        isSended=is_sended,
        isReceived=is_received,
        isReaded=is_readed,
    )
    return {
        "message": "History created successfully.",
        "data": history.id
    }
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
  