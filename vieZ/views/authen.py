from .a import *

class MyInfo(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        if request.user.is_authenticated:
            user = Users.objects.get(oauth_user=request.user)
            return Response(UserSerializer(user).data)
        else:
            return Response({'detail': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)
               
class ZaloMemberLogin(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print("Đang đăng nhập")
            ip=get_client_ip(request)
            key = request.headers.get('StoreKey')
            app_key = request.headers.get('ApplicationKey')
            application = Application.objects.get(client_id=app_key)
            store = UserStore.objects.get(store_id=key)
            user, _ = StoreMember.objects.get_or_create(
                zalo_id=request.data.get('z_id'),
                store=store
            )
            user.last_login=now()
            user.save()
            token = generate_token()
            access_token = AccessToken.objects.create(
                user=user.oauth_user,
                token=token,
                application=application,
                expires=now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
                scope='read write'
            )
            refresh_token_instance = RefreshToken.objects.create(
                user=user.oauth_user,
                token=generate_token(),
                access_token=access_token,
                application=application
            )
            access_token.refresh_token = refresh_token_instance
            access_token.save()
            res_data={
                'access_token': token,
                'refresh_token': refresh_token_instance.token,
                'user': StoreMemberSerializer(user).data,
                'store': UserStoreMemberViewsSerializer(user.store).data
            }
            return Response(res_data, status=status.HTTP_200_OK)
        except StoreMember.DoesNotExist:
            return Response({"message":"Tài khoản không tồn tại"}, 
              status=status.HTTP_400_BAD_REQUEST
            )
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
            
class Login(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print("Đang đăng nhập")
            ip=get_client_ip(request)
            username = request.data.get('username')
            password = request.data.get('password')
            key = request.headers.get('ApplicationKey')
            application = Application.objects.get(client_id=key)
            user=Users.objects.get(username=username)
            user.last_login=now()
            user.save()
            if check_password(password, user.password)==False:
                    return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
            token = generate_token()
            access_token = AccessToken.objects.create(
                user=user.oauth_user,
                token=token,
                application=application,
                expires=now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
                scope='read write'
            )
            refresh_token_instance = RefreshToken.objects.create(
                user=user.oauth_user,
                token=generate_token(),
                access_token=access_token,
                application=application
            )
            access_token.refresh_token = refresh_token_instance
            access_token.save()
            res_data={
                'access_token': token,
                'refresh_token': refresh_token_instance.token
            }
            return Response(res_data, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response({"message":"Tài khoản không tồn tại"}, 
              status=status.HTTP_400_BAD_REQUEST
            )
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
  
class UserFileViewSet(viewsets.ModelViewSet):
    serializer_class = UserFileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagesPagination

    def get_queryset(self):
        user=Users.objects.get(oauth_user=self.request.user)
        return UserFile.objects.filter(user=user).order_by('-uploaded_at')

    def create(self, request, *args, **kwargs):
        user=Users.objects.get(oauth_user=request.user)
        uploaded_files = request.FILES.getlist('file')  # nhận nhiều file cùng lúc
        if not uploaded_files:
            raise serializers.ValidationError({'file': 'Cần ít nhất một file để upload'})
        # Tính tổng dung lượng đã dùng
        used = UserFile.objects.filter(user=user).aggregate(total=models.Sum('file_size'))['total'] or 0
        max_mb = user.userconfigs.plan.max_storage_mb if hasattr(user, 'userconfigs') and user.userconfigs.plan else 0
        max_bytes = max_mb * 1024 * 1024

        saved_instances = []
        total_upload_size = sum(f.size for f in uploaded_files)

        if used + total_upload_size > max_bytes:
            raise serializers.ValidationError({'detail': 'Vượt quá dung lượng cho phép của gói'})

        for file in uploaded_files:
            data = {
                'file': file,
                'file_name': file.name,
                'file_size': file.size,
            }
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            saved_instances.append(serializer.data)

        return Response(saved_instances, status=status.HTTP_201_CREATED)
    def perform_create(self, serializer):
        user = self.request.user
        uploaded_file = self.request.FILES.get('file')

        if not uploaded_file:
            raise serializers.ValidationError({'file': 'File is required'})

        # Kiểm tra dung lượng đã dùng
        used = UserFile.objects.filter(user=user).aggregate(total=models.Sum('file_size'))['total'] or 0
        max_mb = user.userconfigs.plan.max_storage_mb if hasattr(user, 'userconfigs') and user.userconfigs.plan else 0
        if used + uploaded_file.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError({'detail': 'Vượt quá dung lượng cho phép của gói'})
        serializer.save(user=user)
    
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
    
class UserAppsViewSet(viewsets.ModelViewSet):
    queryset = UserApps.objects.all()
    serializer_class = UserAppsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagesPagination
    lookup_field="app_id"
    def perform_create(self, serializer):
        user=Users.objects.get(oauth_user=self.request.user)
        serializer.save(user=user, app_id=generate_unique_app_id())
    def get_queryset(self):
        user=Users.objects.get(oauth_user=self.request.user)
        return UserApps.objects.filter(user=user).order_by('-updated_at')
    def retrieve(self, request, *args, **kwargs):
        return Response(UserAppDetailSerializer(self.get_object()).data)
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