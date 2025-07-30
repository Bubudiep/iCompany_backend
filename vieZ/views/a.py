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

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # Số lượng đối tượng trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 200  # Số lượng đối tượng tối đa trên mỗi trang

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
  