from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from oauthlib.common import generate_token
from oauth2_provider.settings import oauth2_settings
from datetime import timedelta, datetime
from rest_framework import status
from oauth2_provider.models import AccessToken, Application, RefreshToken
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from rest_framework.decorators import action
from django.db.models import Q,F

class StandardPagesPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 200
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class CompanyInfor(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        if key:
            qs_company=Company.objects.filter(appid=key).first()
            if qs_company:
                return Response(CompanySerializer(qs_company).data, 
                    status=status.HTTP_200_OK
                )
        return Response({"message":"Mã công ty không tồn tại"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
class ZaloMemberLogin(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print("Đang đăng nhập")
            ip=get_client_ip(request)
            record=RequestLogin.objects.create(
                ip=ip,
                data=request.data
            )
            qs_company=Company.objects.filter(appid=request.data.get("appid")).first()
            if not qs_company:
                return Response({"message":"Mã công ty không tồn tại"}, 
                  status=status.HTTP_400_BAD_REQUEST
                )
            zaloid=request.data.get("zaloid", None)
            zalonumber=request.data.get("zalonumber", None)
            qs_staff = None
            if zalonumber and zalonumber.startswith("0"):
                zalonumber = f"84{zalonumber[1:]}"
            if not zaloid and not zalonumber:
                qs_staff,_ = ZUsers.objects.get_or_create(
                    company=qs_company, 
                    zaloid="demo_user",
                    zalonumber="demo_user",
                )
            if zaloid and not zalonumber:  # nếu mà có zaloid là auto login
                qs_staff = ZUsers.objects.filter(
                  zaloid=zaloid,
                  company=qs_company
                ).first()
            if not qs_staff and zalonumber: # ko có thì tìm theo sđt
                qs_staff = ZUsers.objects.filter(
                  zalonumber=zalonumber,
                  company=qs_company
                ).first()
                if not qs_staff:
                    return Response(
                      {"message":"Số điện thoại chưa được đăng ký với nhân sự!"}, 
                      status=status.HTTP_400_BAD_REQUEST
                    )
                if qs_staff and not qs_staff.zaloid: # nếu bind với zalo id khác
                    qs_staff.zaloid = zaloid
                    qs_staff.save()
                else: # nếu đã bind
                    return Response(
                      {"message":"Số điện thoại đã được đăng ký với tài khoản khác!"}, 
                      status=status.HTTP_400_BAD_REQUEST
                    )
            if not qs_staff:
                return Response({"message":"Số điện thoại chưa được đăng ký!\nVui lòng liên hệ quản lý bộ phận hoặc phòng nhân sự để được hỗ trợ!"}, 
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
            notify=ZUserNotification.objects.filter(user=qs_staff)
            record.ispass=True
            record.save()
            res_data={
                'access_token': token,
                'refresh_token': refresh_token_instance.token,
                'isvalidated': qs_staff.isvalidated,
                'isadmin': qs_staff.isadmin,
                'isdevelopment': qs_staff.isdevelopment,
                'profile': {
                    'cardid': qs_staff.profile.cardid,
                    'name': qs_staff.profile.name,
                    'phone': qs_staff.profile.phone,
                    'email': qs_staff.profile.email,
                    'avatar': qs_staff.profile.avatar.url if qs_staff.profile.avatar else None,
                    'jobtitle': qs_staff.profile.jobtitle,
                    'department': qs_staff.profile.department,
                },
                'notifications': {
                    'unread_count': notify.filter(is_read=False).count(),
                    'list': [
                        {
                            'id': n.id,
                            'title': n.title,
                            'content': n.content,
                            'is_read': n.is_read,
                            'created_at': n.created_at
                        } for n in notify.order_by('-created_at')[:20]
                    ]
                },
                'company': {
                    'code': qs_staff.company.code,
                    'name': qs_staff.company.name,
                    'appid': qs_staff.company.appid,
                    'hotline': qs_staff.company.hotline,
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

class MyEHSIssueViewSet(viewsets.ModelViewSet):
    queryset = EHSIssue.objects.all()
    serializer_class = EHSIssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagesPagination
    http_method_names = ['patch', 'post', 'get']
    def get_queryset(self):
        user=self.request.user
        return EHSIssue.objects.filter(
          author__oauth_user=user
        ).order_by('-updated_at')
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        page_size = self.request.query_params.get('page_size')
        lastupdate = self.request.query_params.get('last_update')
        if lastupdate:
            queryset = queryset.filter(updated_at__gt=lastupdate)
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class EHSIssueViewSet(viewsets.ModelViewSet):
    queryset = EHSIssue.objects.all()
    serializer_class = EHSIssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagesPagination
    http_method_names = ['patch', 'post', 'get']
    
    def get_serializer(self, *args, **kwargs):
        if self.action in ['list', 'retrieve']:
            return EHSIssueViewSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy() # Copy để có thể chỉnh sửa dữ liệu request
        user = self.request.user
        print('Đang xử lý tạo issue mới trong hàm create')
        area, _ = IssueArea.objects.get_or_create(name=data.get("area"))
        data['area'] = area.id 
        category, _ = IssueCategories.objects.get_or_create(name=data.get("categories"))
        data['categories'] = category.id
        qs_zuser = ZUsers.objects.filter(oauth=user).first()
        data['author'] = qs_zuser.id
        data['company'] = qs_zuser.company.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                issue_instance = serializer.save()
                image_files = request.FILES.getlist('images')
                for f in image_files:
                    EHSImage.objects.create(issue=issue_instance, image=f)
                ZUserNotification.objects.create(
                    user=qs_zuser,
                    app="ehs",
                    target=issue_instance.id,
                    title="Đã gửi báo cáo EHS!" if data.get('private',False)==False else "Đã gửi báo cáo EHS ẩn danh!",
                    content=f"{data['title']}" if data.get('private',False)==False else "Báo cáo thành công!"
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        isme = self.request.query_params.get('isme')
        if isme and isme.lower() == 'true':
            user = self.request.user
            queryset = queryset.filter(author__oauth=user)
        lastupdate = self.request.query_params.get('last_update')
        if lastupdate:
            queryset = queryset.filter(updated_at__gt=lastupdate)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class MailRequestViewSet(viewsets.ModelViewSet):
    queryset = MailRequest.objects.all()
    serializer_class = MailRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagesPagination
    http_method_names = ['patch', 'post', 'get']

    def get_queryset(self):
        return MailRequest.objects.filter(author__oauth=self.request.user).order_by('-created_at')
    def create(self, request, *args, **kwargs):
        data = request.data.copy() # Copy để có thể chỉnh sửa dữ liệu request
        user = self.request.user
        qs_zuser = ZUsers.objects.filter(oauth=user).first()
        data['author'] = qs_zuser.id
        data['company'] = qs_zuser.company.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        mail=serializer.save()
        ZUserNotification.objects.create(
            user=qs_zuser,
            app="mail",
            target=mail.id,
            title="Đã gửi thư góp ý!" if data.get('isAnonymous',False)==False else "Đã gửi thư góp ý ẩn danh!",
            content=f"{data['subject']}" if data.get('isAnonymous',False)==False else "Thư đã được gửi!"
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        lastupdate = self.request.query_params.get('last_update')
        if lastupdate:
            queryset = queryset.filter(updated_at__gt=lastupdate)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class QNARequestViewSet(viewsets.ModelViewSet):
    queryset = QNARequest.objects.all()
    serializer_class = QNARequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagesPagination
    http_method_names = ['patch', 'post', 'get']

    def get_queryset(self):
        user = self.request.user
        return QNARequest.objects.filter(Q(author__oauth=user)|Q(answer_by__isnull=False)).distinct().order_by('-created_at')
    
    def get_serializer(self, *args, **kwargs):
        if self.action in ['list', 'retrieve']:
            return QNARequestViewSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy() # Copy để có thể chỉnh sửa dữ liệu request
        user = self.request.user
        qs_zuser = ZUsers.objects.filter(oauth=user).first()
        data['author'] = qs_zuser.id
        data['company'] = qs_zuser.company.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        qna=serializer.save()
        ZUserNotification.objects.create(
            user=qs_zuser,
            app="qna",
            target=qna.id,
            title="Đã gửi câu hỏi!" if data.get('isAnonymous',False)==False else "Đã gửi câu hỏi ẩn danh!",
            content=f"{data['question']}" if data.get('isAnonymous',False)==False else "Đã đặt câu hỏi!"
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        lastupdate = self.request.query_params.get('last_update')
        if lastupdate:
            queryset = queryset.filter(updated_at__gt=lastupdate)
        isme = self.request.query_params.get('isme')
        if isme and isme.lower() == 'true':
            user = self.request.user
            queryset = queryset.filter(author__oauth=user)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class ZUserNotificationViewSet(viewsets.ModelViewSet):
    queryset = ZUserNotification.objects.all()
    serializer_class = ZUserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagesPagination
    http_method_names = ['get']

    def retrieve(self, request, *args, **kwargs):
        notif=self.get_object()
        if notif.is_read==False:
            notif.is_read=True
            notif.save()
        return super().retrieve(request, *args, **kwargs)
    
    def get_queryset(self):
        user = self.request.user
        return ZUserNotification.objects.filter(user__oauth=user).order_by('-created_at')
    
    def get_serializer(self, *args, **kwargs):
        if self.action in ['list', 'retrieve']:
            return ZUserNotificationSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        lastupdate = self.request.query_params.get('last_update')
        if lastupdate:
            queryset = queryset.filter(updated_at__gt=lastupdate)
        unread = queryset.filter(is_read=False).count()
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_custom_paginated_response(serializer.data, unread)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def get_custom_paginated_response(self, data, unread_count):
        """
        Helper để chèn thêm field vào response phân trang mặc định
        """
        response = self.get_paginated_response(data)
        response.data['unread_count'] = unread_count
        return response