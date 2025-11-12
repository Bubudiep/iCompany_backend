from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from oauth2_provider.models import Application, AccessToken
from oauth2_provider.settings import oauth2_settings
from datetime import timedelta
from django.utils import timezone
import secrets
from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q,F
from django.contrib.auth.hashers import check_password

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # Số lượng đối tượng trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 200  # Số lượng đối tượng tối đa trên mỗi trang

class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = HRUser.objects.get(user=request.user)
        return Response(UserSerializer(user).data)
    
class LoginView(APIView):
    permission_classes = [AllowAny]#
    def post(self, request):
        expires_time=1000*60*60*24*15
        username = request.data.get("username")
        password = request.data.get("password")
        key = request.headers.get('ApplicationKey')
        try:
            qs_user = HRUser.objects.get(username=username)
            oauth_user = qs_user.user
            if check_password(password, qs_user.password)==False:
                return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
            app = Application.objects.get(client_id=key)
            expires = timezone.now() + timedelta(seconds=expires_time)
            access_token = AccessToken.objects.create(
                user=oauth_user,
                application=app,
                expires=expires,
                token=secrets.token_urlsafe(32),
                scope="read write"
            )
            return Response({
                "access_token": access_token.token,
                "expires_in": expires,
                "token_type": "Bearer",
            })
        except Application.DoesNotExist:
            return Response({"detail": "App chưa được đăng ký!"}, status=status.HTTP_400_BAD_REQUEST)
        except HRUser.DoesNotExist:
            return Response({"detail": "Tài khoản chưa được đăng ký!"}, status=status.HTTP_400_BAD_REQUEST)
        
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']
    def get_queryset(self):
        qsuser=HRUser.objects.get(user=self.request.user)
        return UserProfile.objects.filter(user=qsuser)
        