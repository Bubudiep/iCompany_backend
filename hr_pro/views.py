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
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q,F
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404

token_expires_time=1000*60*60*24*15
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
        username = request.data.get("username")
        password = request.data.get("password")
        key = request.headers.get('ApplicationKey')
        try:
            qs_user = HRUser.objects.get(username=username)
            oauth_user = qs_user.user
            if check_password(password, qs_user.password)==False:
                return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
            app = Application.objects.get(client_id=key)
            expires = timezone.now() + timedelta(seconds=token_expires_time)
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
        
class DangkyView(APIView):
    permission_classes = [AllowAny]#
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        key = request.headers.get('ApplicationKey')
        try:
            qs_duplicate = HRUser.objects.filter(username=username).count()
            if qs_duplicate>0:
                return Response({'detail': 'Tài khoản đã tồn tại'}, status=status.HTTP_401_UNAUTHORIZED)
            qs_user = HRUser.objects.create(username=username,password=password)
            oauth_user = qs_user.user
            app = Application.objects.get(client_id=key)
            expires = timezone.now() + timedelta(seconds=token_expires_time)
            access_token = AccessToken.objects.create(
                user=oauth_user,application=app,expires=expires,
                token=secrets.token_urlsafe(32),scope="read write"
            )
            return Response({
                "access_token": access_token.token,
                "expires_in": expires,
                "token_type": "Bearer",
            })
        except Application.DoesNotExist:
            return Response({"detail": "App chưa được đăng ký!"}, status=status.HTTP_400_BAD_REQUEST)
        
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']
    def get_queryset(self):
        qsuser=HRUser.objects.get(user=self.request.user)
        return UserProfile.objects.filter(user=qsuser)

class BaivietViewSet(viewsets.ModelViewSet):
    serializer_class = BaivietSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get", "post"]
    pagination_class = StandardResultsSetPagination
    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    def get_queryset(self):
        queryset = Baiviet.objects.filter(is_verified=True)
        queryset = queryset.annotate(
            likes_count=Count('likes', distinct=True),
            shares_count=Count('shares', distinct=True),
            views_count=Count('vieweds', distinct=True),
        ).select_related('user').order_by('-created_at')
        return queryset
    def perform_create(self, serializer):
        qsuser=HRUser.objects.get(user=self.request.user)
        qs_profile=UserProfile.objects.get(user=qsuser)
        if qs_profile.level in ['admin','support','company']:
            serializer.save(user=qsuser,is_verified=True)
        else:
            serializer.save(user=qsuser)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        show_ids = self.request.query_params.get("show_ids")
        if show_ids:
          queryset=queryset.exclude(id__in=show_ids.split(','))
        page_size = self.request.query_params.get("page_size")
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if request.user.is_authenticated:
            try:
                hr_user = HRUser.objects.get(user=request.user) 
            except HRUser.DoesNotExist:
                hr_user = None 
            if hr_user:
                print(hr_user)
                items_to_view = page if page is not None else []
                for baiviet in items_to_view:
                    baiviet.vieweds.add(hr_user)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class KhuCongNghiepViewSet(viewsets.ModelViewSet):
    queryset = KhuCongNghiep.objects.all()
    serializer_class = KhuCongNghiepSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get"]
    pagination_class = StandardResultsSetPagination
    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        max_update_id = self.request.query_params.get("max_id")
        if max_update_id!="0":
            queryset=queryset.filter(updated_at__gt=max_update_id)
        page_size = self.request.query_params.get("page_size")
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CompanyListsViewSet(viewsets.ModelViewSet):
    queryset = CompanyLists.objects.all()
    serializer_class = CompanyListsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get","post","patch","delete"]
    pagination_class = StandardResultsSetPagination
    
    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def destroy(self, request, *args, **kwargs):
        user=request.user
        try:
            qs_profile=UserProfile.objects.get(user__user=user,level__in=["admin"])
            if qs_profile:
                instance=self.get_object()
                instance.soft_delete=True
                instance.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        user=request.user
        try:
            qs_profile=UserProfile.objects.get(user__user=user,level__in=["admin","support"])
            if qs_profile:
                return super().create(request, *args, **kwargs)
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        user=request.user
        try:
            qs_profile=UserProfile.objects.get(user__user=user,level__in=["admin","support"])
            if qs_profile:
                return super().update(request, *args, **kwargs)
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        max_update_id = self.request.query_params.get("max_id")
        if max_update_id!="0":
            queryset=queryset.filter(updated_at__gt=max_update_id)
        page_size = self.request.query_params.get("page_size")
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class AnhSliceViewSet(viewsets.ModelViewSet):
    queryset = AnhSlice.objects.all()
    serializer_class = AnhSliceSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["get"]
    pagination_class = StandardResultsSetPagination
    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page_size = self.request.query_params.get("page_size")
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class BaivietTuyendungTagsViewSet(viewsets.ModelViewSet):
    queryset = BaivietTuyendungTags.objects.all()
    serializer_class = BaivietTuyendungTagsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get","post"]
    pagination_class = StandardResultsSetPagination
    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        max_update_id = self.request.query_params.get("max_id")
        if max_update_id!="0":
            queryset=queryset.filter(updated_at__gt=max_update_id)
        page_size = self.request.query_params.get("page_size")
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class BaivietTuyendungViewSet(viewsets.ModelViewSet):
    queryset = BaivietTuyendung.objects.all()
    serializer_class = BaivietTuyendungSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get","post","patch",'delete']
    pagination_class = StandardResultsSetPagination
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]
        filter_kwargs = {}
        if lookup_value.isdigit():
            filter_kwargs = {'id': lookup_value}
        else:
            filter_kwargs = {'code': lookup_value}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj
    
    def get_queryset(self):
        queryset = BaivietTuyendung.objects.all()
        queryset = queryset.annotate(
            apply_count=Count('applybaiviettuyendung')
        )
        return queryset
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'ungtuyen','share']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    def destroy(self, request, *args, **kwargs):
        user=request.user
        try:
            qs_profile=UserProfile.objects.get(user__user=user,level__in=["admin","support"])
            if qs_profile:
                instance=self.get_object()
                instance.soft_delete=True
                instance.save()
                return Response(BaivietTuyendungSerializer(instance).data)
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(f"{e}")
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)
    def perform_create(self, serializer):
        qsuser=HRUser.objects.get(user=self.request.user)
        serializer.save(user=qsuser)
    def retrieve(self, request, *args, **kwargs):
        instance=self.get_object()
        instance.view_count=instance.view_count+1
        if request.user.is_authenticated:
            qs_usr=HRUser.objects.filter(user=request.user).first()
            if qs_usr:
                instance.vieweds.add(qs_usr)
        instance.save()
        return super().retrieve(request, *args, **kwargs)
    @action(detail=True, methods=["post"], permission_classes=[permissions.AllowAny])
    def share(self, request, pk=None):
        instance = self.get_object()
        instance.share_count= instance.share_count+1
        instance.save()
        return Response(BaivietTuyendungSerializer(instance).data)
    @action(detail=True, methods=["post"], permission_classes=[permissions.AllowAny])
    def ungtuyen(self, request, pk=None):
        instance = self.get_object()
        user=None
        try:
            if request.user.is_authenticated:
                user=HRUser.objects.get(user=request.user)
            name=request.data.get('name',None)
            phone=request.data.get('phone',None)
            invent_code=request.data.get('invent_code',None)
            nguoigioithieu=None
            if phone[0]!=0 and len(phone)!=10:
                return Response({'detail':"Số điện thoại không hợp lệ!"},status=status.HTTP_403_FORBIDDEN)
            if invent_code:
                qs_profile=UserProfile.objects.filter(invent_code=invent_code).first()
                if qs_profile:
                    nguoigioithieu=qs_profile.user
            if name and phone:
                ungtuyen=ApplyBaivietTuyendung.objects.create(
                    baiviet=instance,
                    nguoigioithieu=nguoigioithieu,
                    nguoiungtuyen=user,
                    sodienthoai=phone,
                    hovaten=name,
                    noidungungtuyen="Ứng tuyển qua web mobile!"
                )
                return Response(BaivietTuyendungSerializer(instance).data)
            else:
                return Response({'detail':"Không có tên hoặc số điện thoại"},status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(f"{e}")
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)
    @action(detail=True, methods=["post"])
    def remove_image(self, request, pk=None):
        instance = self.get_object()
        user=request.user
        try:
            qs_profile=UserProfile.objects.get(user__user=user,level__in=["admin","support"])
            if qs_profile:
                images=instance.images.all()
                image=images.get(id=request.data.get('id'))
                image.delete()
                return Response(BaivietTuyendungSerializer(instance,context={'request':request}).data)
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(f"{e}")
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)
    def create(self, request, *args, **kwargs):
        user=request.user
        if request.data.get('title','') == '':
            return Response({'detail':"Chưa nhập tiêu đề"},status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('noidungbosung','') == '':
            return Response({'detail':"Chưa nhập mô tả công việc"},status=status.HTTP_400_BAD_REQUEST)
        try:
            qs_profile=UserProfile.objects.get(user__user=user,level__in=["admin","support"])
            if qs_profile:
                return super().create(request, *args, **kwargs)
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'detail':"Không có quyền"},status=status.HTTP_403_FORBIDDEN)
    def update(self, request, *args, **kwargs):
        user=request.user
        try:
            qs_profile=UserProfile.objects.get(user__user=user,level__in=["admin","support"])
            if qs_profile:
                return super().update(request, *args, **kwargs)
            return Response({'detail':"Không có quyền 1"},status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(f"{e}")
            return Response({'detail':"Không có quyền 2"},status=status.HTTP_403_FORBIDDEN)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        max_update_id = self.request.query_params.get("max_id")
        if max_update_id and max_update_id!="0":
            queryset=queryset.filter(updated_at__gt=max_update_id)
        
        code = self.request.query_params.get("code")
        if code:
            queryset=queryset.filter(code=code)
        page_size = self.request.query_params.get("page_size")
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)