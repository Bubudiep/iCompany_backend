from django.shortcuts import render
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from oauthlib.common import generate_token
from oauth2_provider.settings import oauth2_settings
from datetime import timedelta, datetime
from rest_framework import status
from oauth2_provider.models import AccessToken, Application, RefreshToken

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class ZaloMemberLogin(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print("Đang đăng nhập")
            ip=get_client_ip(request)
            qs_company=Company.objects.filter(appid=request.data.get("appid")).first()
            if not qs_company:
                return Response({"message":"Mã công ty không tồn tại"}, 
                  status=status.HTTP_400_BAD_REQUEST
                )
            zaloid=request.data.get("zaloid", None)
            zalonumber=request.data.get("zalonumber", None)
            qs_staff = None
            if zaloid:
                qs_staff = ZUsers.objects.filter(
                  zaloid=zaloid,
                  company=qs_company
                ).first()
            if not qs_staff and zalonumber:
                qs_staff = ZUsers.objects.filter(
                  zalonumber=zalonumber,
                  company=qs_company
                ).first()
                if qs_staff and not qs_staff.zaloid:
                    qs_staff.zaloid = zaloid
                    qs_staff.save()
            if not qs_staff:
                return Response({"message":"Số điện thoại chưa được đăng ký"}, 
                  status=status.HTTP_400_BAD_REQUEST
                )
            application = Application.objects.get(name="Zalo")
            token = generate_token()
            access_token = AccessToken.objects.create(
                user=qs_staff.oauth,
                token=token,
                application=application,
                expires=now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
                scope='read write'
            )
            refresh_token_instance = RefreshToken.objects.create(
                user=qs_staff.oauth,
                token=generate_token(),
                access_token=access_token,
                application=application
            )
            access_token.refresh_token = refresh_token_instance
            access_token.save()
            res_data={
                'access_token': token,
                'refresh_token': refresh_token_instance.token,
                'isvalidated': qs_staff.isvalidated,
                'isadmin': qs_staff.isadmin,
                'isdevelopment': qs_staff.isdevelopment,
                'profile': {
                    'name': qs_staff.profile.name,
                    'phone': qs_staff.profile.phone,
                    'email': qs_staff.profile.email,
                    'avatar': qs_staff.profile.avatar.url if qs_staff.profile.avatar else None,
                    'jobtitle': qs_staff.profile.jobtitle,
                    'department': qs_staff.profile.department,
                },
                'company': {
                    'code': qs_staff.company.code,
                    'name': qs_staff.company.name,
                    'appid': qs_staff.company.appid,
                }
            }
            return Response(res_data, status=status.HTTP_200_OK)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            return Response(
              {
                "message":"Phát sinh lỗi khi đăng nhập!",
                "possition":f"{file_name}_{lineno}",
                "detail":str(e)
              }, 
              status=status.HTTP_400_BAD_REQUEST
            )
        