import sys
import os
from django.conf import settings
from ..models import *
from ..serializers import *
from ..filters import *
from datetime import timedelta
from django.utils.timezone import now
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
from django.db.models import Q,F
from rest_framework.decorators import action
from pytz import timezone
from django.db import transaction

myzone = timezone('Asia/Ho_Chi_Minh')
def generate_response_json(result:str, message:str, data:dict={}):
    return {"result": result, "message": message, "data": data}
  
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # Số lượng đối tượng trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 200  # Số lượng đối tượng tối đa trên mỗi trang