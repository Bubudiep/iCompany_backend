import sys
import os
from .serializers import *
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
from django.db import transaction
from django.utils.crypto import get_random_string
import pandas as pd
from rest_framework.parsers import MultiPartParser
from io import BytesIO
from django.http import HttpResponse
  
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # Số lượng đối tượng trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 200  # Số lượng đối tượng tối đa trên mỗi trang

def generate_response_json(result:str, message:str, data:dict={}):
    return {"result": result, "message": message, "data": data}
  
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
  
class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print("Đang đăng nhập")
            ip=get_client_ip(request)
            username = request.data.get('username')
            password = request.data.get('password')
            if username is None or password is None:
                return Response(data={'detail':'Vui lòng nhập đầy đủ thông tin đăng nhập!'}, 
                  status=status.HTTP_400_BAD_REQUEST)
            token = generate_token()
            application = Application.objects.get(client_id='48MghDAMhSXJoPZKwQ7BZoRVIjQJLowv7QFrtT08')
            user=ZaloUser.objects.get(username=username)
            if check_password(password, user.password)==False:
                return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
            access_token = AccessToken.objects.create(
                user=user.user,
                token=token,
                application=application,
                expires=now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
                scope='read write'
            )
            refresh_token_instance = RefreshToken.objects.create(
                user=user.user,
                token=generate_token(),
                access_token=access_token,
                application=application
            )
            access_token.refresh_token = refresh_token_instance
            access_token.save()
            return Response({
                'access_token': token,
                'refresh_token': refresh_token_instance.token,
                'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                'token_type': 'Bearer',
                'scope': access_token.scope,
            }, status=status.HTTP_200_OK)
        except ZaloUser.DoesNotExist:
            return Response({'detail': 'Tài khoản không tồn tại'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)

class GetUserAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    
    def get(self, request):
        if request.user.is_authenticated:
            user=request.user
            zuser=ZaloUser.objects.get(user=user)
            try:
                qs_profile,_=ZaloUserProfile.objects.get_or_create(user=zuser)
                qs_group=UserGroup.objects.filter(member=zuser)
                qs_friend=ZaloUserProfile.objects.filter(user__id__in=qs_group.values_list('member__id', flat=True))
                qs_type=ApproveType.objects.all()
                qs_item=ApproveItem.objects.filter(author=zuser)
                approve_not_read=0
                alert_not_read=0
                for group in qs_group:
                  qs_lastcheck,_=LastCheckGroup.objects.get_or_create(user=zuser,group=group)
                  qs_new=ApproveItem.objects.filter(
                    group=group,
                    created_at__gt=qs_lastcheck.last_check
                  )
                  approve_not_read+=qs_new.count()
                return Response({
                    'id': zuser.id,
                    'profile': ZaloUserProfileSerializer(qs_profile).data,
                    'type': ApproveTypeSerializer(qs_type,many=True).data,
                    'group': UserGroupSerializer(qs_group,many=True).data,
                    'request': ApproveItemSerializer(qs_item,many=True).data,
                    'friend': ZaloUserProfileSerializer(qs_friend,many=True).data,
                    'unread': {
                        'alert_unread': alert_not_read,
                        'item_unread': approve_not_read
                    }
                }, status=status.HTTP_200_OK)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                lineno = exc_tb.tb_lineno
                file_path = exc_tb.tb_frame.f_code.co_filename
                file_name = os.path.basename(file_path)
                res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
                print(f"{res_data}")
                return Response({'detail': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)

class ZaloUserProfileViewSet(viewsets.ModelViewSet):
    queryset =ZaloUserProfile.objects.all()
    serializer_class =ZaloUserProfilesSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get','patch']
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,OrderingFilter)
    ordering_fields = ['created_at', 'last_have_message_at']
    def get_queryset(self):
        user = self.request.user
        return ZaloUserProfile.objects.filter(user__user=user)
      
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data)

class UserGroupViewSet(viewsets.ModelViewSet):
    queryset =UserGroup.objects.all()
    serializer_class =UserGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get','post','patch']
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,OrderingFilter)
    ordering_fields = ['created_at', 'last_have_message_at']
    def get_queryset(self):
        user = self.request.user
        return UserGroup.objects.filter(member__user=user)
    
    def retrieve(self, request, *args, **kwargs):
        group = self.get_object()
        return Response(UserGroupsSerializer(group).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def add_type(self, request, pk=None):
        user = self.request.user
        zuser=ZaloUser.objects.get(user=user)
        group = self.get_object()
        if zuser==group.host:
            dt_name=request.data.get('name',None)
            dt_description=request.data.get('description',None)
            dt_approver=request.data.get('approver',[])
            new_type,_=ApproveType.objects.get_or_create(group=group,
                                                         name=dt_name,
                                                         description=dt_description,
                                                         user=zuser)
            new_type.approver.set(dt_approver)
            new_type.save()
            return Response(UserGroupsSerializer(group).data,
                            status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Bạn không có quyền thực hiện thao tác này.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        user = self.request.user
        zuser=ZaloUser.objects.get(user=user)
        group = self.get_object()
        if zuser==group.host:
            dt_users=request.data.get('users',None)
            for member in dt_users:
                qs_member=ZaloUser.objects.get(id=member)
                isSuccess=False
                recordDetails=""
                if qs_member not in group.member.all():
                    group.member.add(qs_member)
                    group.save()
                    isSuccess=True
                else:
                    recordDetails="Thành viên đã có trong danh sách"
                UserGroupRecord.objects.create(user=zuser,
                                                group=group,
                                                success=isSuccess,
                                                detail=recordDetails,
                                                action="add_member",
                                                comment="Thêm thành viên mới",
                                                target=qs_member)
            return Response(UserGroupsSerializer(group).data,
                            status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Bạn không có quyền thực hiện thao tác này.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'])
    def add_request(self, request, pk=None):
        user = self.request.user
        zuser=ZaloUser.objects.get(user=user)
        group = self.get_object()
        if zuser in group.member.all():
            dt_title=request.data.get('title',None)
            dt_amount=request.data.get('amount',None)
            dt_description=request.data.get('description',None)
            dt_picture_base64=request.data.get('picture_base64',None)
            dt_picture_link=request.data.get('picture_link',None)
            dt_sendto=request.data.get('sendto',[])
            dt_types=request.data.get('types',[])
            cr_item=ApproveItem.objects.create(
                title=dt_title,
                amount=dt_amount,
                description=dt_description,
                picture_base64=dt_picture_base64,
                picture_link=dt_picture_link,
                author=ZaloUser.objects.get(user=user),
                group=group
            )
            for sendto in dt_sendto:
                cr_item.sendto.add(ZaloUser.objects.get(id=sendto))
            for types in dt_types:
                cr_item.types.add(ApproveType.objects.get(id=types))
            cr_item.save()
            return Response(ApproveItemsSerializer(cr_item).data,
                            status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Bạn không có quyền thực hiện thao tác này.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
      
    def create(self, request, *args, **kwargs):
        user = self.request.user
        zuser=ZaloUser.objects.get(user=user)
        data = request.data.copy()
        members = data.pop('member', [])
        approvers = data.pop('approver', [])
        amount_approvers = data.pop('amount_approver', [])
        payment_approvers = data.pop('payment_approver', [])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save(host=zuser)
        if members:
            group.member.set(members)
        group.member.add(zuser)
        if approvers:
            group.approver.set(approvers)
        if amount_approvers:
            group.amount_approver.set(amount_approvers)
        if payment_approvers:
            group.payment_approver.set(payment_approvers)
        group.save()
        return Response(self.get_serializer(group).data, status=status.HTTP_201_CREATED)
        
    def update(self, request, *args, **kwargs):
        user = self.request.user
        zuser=ZaloUser.objects.get(user=user)
        group = self.get_object()
        if zuser!=group.host:
            return Response({'detail': 'Bạn không phải chủ Group'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class ApproveItemViewSet(viewsets.ModelViewSet):
    queryset =ApproveItem.objects.all()
    serializer_class =ApproveItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get','post','patch']
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        user = self.request.user
        return ApproveItem.objects.filter(group__member__user=user)
    
    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="Không tìm thấy bản ghi phê duyệt.")
        
    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        user = self.request.user
        zuser=ZaloUser.objects.get(user=user)
        item = self.get_object()
        if zuser==item.author:
            if item.status=="pending" or item.status=="cancel":
                item.delete()
                return Response({'detail': 'Thành công'}, 
                                status=status.HTTP_200_OK)
            else:
                return Response({'detail': f'Trạng thái hiện tại là {item.status}'}, 
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Bạn không có quyền thực hiện thao tác này.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=True, methods=['post'])
    def payout(self, request, pk=None):
        user = self.request.user
        zuser=ZaloUser.objects.get(user=user)
        item = self.get_object()
        if item.amount==0:
            return Response({'detail': 'Không cần giải ngân'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        if item.status=="pending":
            return Response({'detail': 'Chưa được phê duyệt'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        if item.status!="approved":
            return Response({'detail': 'Đã hoàn thành'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        # kiểm tra có trong nhóm thành viên không
        if zuser not in item.group.member.all():
            return Response({'detail': 'Bạn không có quyền thực hiện thao tác này.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
            
        # Kiểm tra type có approve không
        can_approve=[]
        for typ in item.types.all():
            for apv_type in typ.payment_approver.all():
                can_approve.append(apv_type.id)
        if len(can_approve)>0: # xem có phân loại gì đặc biệt không
            if zuser.id not in can_approve:
                return Response({'detail': 'Bạn không có quyền giải ngân cho phê duyệt loại này'}, 
                                status=status.HTTP_400_BAD_REQUEST)
        elif item.group.payment_approver.all().count()>0:
            if zuser not in item.group.payment_approver.all():
                    return Response({'detail': 'Bạn không có quyền giải ngân cho phê duyệt này.'}, 
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            if zuser not in item.group.approver.all():
                    return Response({'detail': 'Bạn không có quyền giải ngân cho phê duyệt này.'}, 
                                    status=status.HTTP_400_BAD_REQUEST)
        cr_hist=ApproveItemRecord.objects.create(item=item,
                                                 action='disburse',
                                                 user=zuser,
                                                 comment=request.data.get('comment',None))
        if cr_hist:
            item.status='disbursed'
            item.save()
            cr_hist=ApproveItemRecord.objects.create(item=item,
                action='complete',
                user=zuser,
                comment='Tự động complete'
            )
            item.status='complete'
            item.save()
            return Response(ApproveItemsSerializer(item).data,status=status.HTTP_200_OK)
        return Response({'detail': 'Bạn không có quyền thực hiện thao tác này.'},status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        user = self.request.user
        zuser=ZaloUser.objects.get(user=user)
        item = self.get_object()
        if item.status!="complete":
            return Response({'detail': 'Phê duyệt chưa hoàn thành'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        # kiểm tra có trong nhóm thành viên không
        if zuser!=item.author and zuser!=item.group.host:
            return Response({'detail': 'Chỉ người tạo phê duyệt hoặc admin mới có quyền đóng'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        ApproveItemRecord.objects.create(item=item,
            action='close',
            user=zuser,
            comment=request.data.get('feedback',None)
        )
        item.rate=request.data.get('rate',0)
        item.feedback=request.data.get('feedback',None)
        item.status="close"
        item.save()
        return Response(ApproveItemsSerializer(item).data,status=status.HTTP_200_OK)
            
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = self.request.user
        zuser=ZaloUser.objects.get(user=user)
        item = self.get_object()
        if item.status!="pending":
            return Response({'detail': 'Không cần phê duyệt nữa'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        # kiểm tra có trong nhóm thành viên không
        if zuser not in item.group.member.all():
            return Response({'detail': 'Bạn không có quyền thực hiện thao tác này.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
            
        # Kiểm tra type có approve không
        
        can_approve=[]
        for typ in item.types.all():
            if item.amount!=0 and typ.amount_approver.all().count()!=0:
                for apv_type in typ.amount_approver.all():
                    can_approve.append(apv_type.id)
            else:
                for apv_type in typ.approver.all():
                    amount_approver.append(apv_type.id)
        if item.sendto.all().count()>0: # xem có gửi cho ai không
            if zuser not in item.sendto.all():
                return Response({'detail': 'Phê duyệt này được gửi cho người khác'}, 
                                status=status.HTTP_400_BAD_REQUEST)
        elif len(can_approve)>0: # xem có phân loại gì đặc biệt không
            if zuser.id not in can_approve:
                return Response({'detail': 'Bạn không có quyền phê duyệt loại này'}, 
                                status=status.HTTP_400_BAD_REQUEST)
        else: # xem có quyền phê duyệt không
            if item.amount!=0 and item.group.amount_approver.all().count()!=0:
                if zuser not in item.group.amount_approver.all():
                    return Response({'detail': 'Bạn không có quyền duyệt đơn có chi phí'}, 
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                if zuser not in item.group.approver.all():
                    return Response({'detail': 'Bạn không có quyền thực hiện thao tác này.'}, 
                                    status=status.HTTP_400_BAD_REQUEST)
        cr_hist=ApproveItemRecord.objects.create(item=item,
                                                 action='approve',
                                                 user=zuser,
                                                 comment=request.data.get('comment',None))
        if cr_hist:
            item.status='approved'
            item.save()
            if item.amount==0:
                cr_hist=ApproveItemRecord.objects.create(item=item,
                                                    action='complete',
                                                    user=zuser,
                                                    comment='Tự động complete (không cần giải ngân)')
                item.status='complete'
                item.save()
            return Response(ApproveItemsSerializer(item).data,
                            status=status.HTTP_200_OK)
        return Response({'detail': 'Bạn không có quyền thực hiện thao tác này.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=True, methods=['post'])
    def effect(self, request, pk=None):
        user = self.request.user
        zuser=ZaloUser.objects.get(user=user)
        item = self.get_object()
        if zuser in item.group.member.all():
            dt_emoji=request.data.get('emoji',None)
            qs_emj,_=ApproveItemEmoji.objects.get_or_create(item=item,user=zuser,emoji=dt_emoji)
            qs_emj.count=qs_emj.count+1
            qs_emj.save()
            return Response(ApproveItemsSerializer(item).data,
                            status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Bạn không có quyền thực hiện thao tác này.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        user = self.request.user
        zuser=ZaloUser.objects.get(user=user)
        item = self.get_object()
        if zuser in item.group.member.all():
            dt_message=request.data.get('message',None)
            dt_reply=request.data.get('reply',None)
            if dt_reply:
                dt_reply=ApproveItemMessage.objects.get(item=item,id=dt_reply)
            new_chat=ApproveItemMessage.objects.create(item=item,
                                            user=zuser,
                                            message=dt_message,
                                            reply=dt_reply)
            return Response(ApproveItemsSerializer(item).data,
                            status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Bạn không có quyền thực hiện thao tác này.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
            
    def retrieve(self, request, *args, **kwargs):
        item = self.get_object()
        return Response(ApproveItemsSerializer(item).data,
                        status=status.HTTP_200_OK)
        
    def update(self, request, *args, **kwargs):
        item = self.get_object()
        
        zuser=ZaloUser.objects.get(user=user)
        item = self.get_object()
        if zuser==item.author:
            if item.status=="pending" or item.status=="cancel" or item.status=="reject":
                # chỉ sửa được khi đang pending hoặc đã cancel hoặc đã reject
                # Đã duyệt, đã giải ngân thì không sửa được nữa
                return super().update(request, *args, **kwargs)
            else:
                return Response({"detail":"Trạng thái hiện tại không được sửa!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({"detail":"Không được phép tạo!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
    def create(self, request, *args, **kwargs):
        return Response({"detail":"Không được phép tạo!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        group = self.request.query_params.get('group')
        if group is not None:
            queryset=queryset.filter(group__id=group)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)