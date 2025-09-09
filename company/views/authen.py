from .a import *

class PermissionAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        query = request.query_params.get('p', '').strip()
        if request.user.is_authenticated and query:
            user=request.user
            return check_permission(user,query)
        
class LoginOAuthLTEAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print("Đang đăng nhập")
            ip=get_client_ip(request)
            username = request.data.get('username')
            password = request.data.get('password')
            client_id = request.data.get('client_id')
            key = request.headers.get('ApplicationKey')
            token = generate_token()
            application = Application.objects.get(client_id=client_id)
            company_instance=Company.objects.get(key=key)
            user=CompanyUser.objects.get(username=username,company=company_instance )
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
            record_user_action(function_name="login",
                               action_name="login",
                               ip_action=ip,
                               staff=user,
                               title="Đăng nhập",
                               message=f"Đăng nhập thành công tại ip {ip}",
                               is_hidden=True)
            access_token.refresh_token = refresh_token_instance
            access_token.save()
            staff=CompanyStaff.objects.get(user=user)
            LastCheckAPI.objects.update_or_create(
                function_name='login',
                user=staff,
                defaults={'last_read_at': now()}
            )
            res_data={
                'access_token': token,
                'refresh_token': refresh_token_instance.token,
                'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                'token_type': 'Bearer',
                'scope': access_token.scope,
            }
            print(f"{res_data}")
            return Response(res_data, status=status.HTTP_200_OK)
        except Application.DoesNotExist:
            return Response({'detail': "App chưa được đăng ký hoặc chưa kích hoạt!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
           
class LoginOAuth2APIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print("Đang đăng nhập")
            ip=get_client_ip(request)
            username = request.data.get('username')
            password = request.data.get('password')
            key = request.headers.get('ApplicationKey')
            token = generate_token()
            application = Application.objects.get(client_id='48MghDAMhSXJoPZKwQ7BZoRVIjQJLowv7QFrtT08')
            #OfCTXBjo9mUmvzurHSZaQa52lQLfZ8Qu5XPDbKnR4h1vNQEIEQDGiCu4iH5QrGGiMYLjevnCr2X3sF3jvk8jhn59eQaTCv7GAArEL1CMz45OwR9CZRMvBKwr4nU0iNh7
            company_instance=Company.objects.get(key=key)
            user=CompanyUser.objects.get(username=username,company=company_instance )
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
            record_user_action(function_name="login",
                               action_name="login",
                               ip_action=ip,
                               staff=user,
                               title="Đăng nhập",
                               message=f"Đăng nhập thành công tại ip {ip}",
                               is_hidden=True)
            access_token.refresh_token = refresh_token_instance
            access_token.save()
            staff=CompanyStaff.objects.get(user=user)
            LastCheckAPI.objects.update_or_create(
                function_name='login',
                user=staff,
                defaults={'last_read_at': now()}
            )
            res_data={
                'access_token': token,
                'refresh_token': refresh_token_instance.token,
                'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                'token_type': 'Bearer',
                'scope': access_token.scope,
                'user': CompanyStaffSerializer(staff).data
            }
            print(f"{res_data}")
            return Response(res_data, status=status.HTTP_200_OK)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
           
class GetUserLTEView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
                qs_profile,_=CompanyStaffProfile.objects.get_or_create(staff=qs_staff)
                return Response({
                    "staff":CompanyStaffLTESerializer(qs_staff).data,
                    "profile":CompanyStaffProfileSerializer(qs_profile).data
                }, status=status.HTTP_200_OK)
            except CompanyStaff.DoesNotExist:
                return Response({'detail': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
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
        
class GetCompanyLTEView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
                return Response(CompanySerializer(qs_staff.company).data, status=status.HTTP_200_OK)
            except CompanyStaff.DoesNotExist:
                return Response({'detail': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
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
        
class GetCompanyLTEView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
                return Response(CompanyLTESerializer(qs_staff.company).data, status=status.HTTP_200_OK)
            except CompanyStaff.DoesNotExist:
                return Response({'detail': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
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
        
class GetOperatorLTEView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
                ops = CompanyOperator.objects.filter(company=qs_staff.company)
                return Response(CompanyOperatorLTESerializer(ops, many=True).data, status=status.HTTP_200_OK)
            except CompanyStaff.DoesNotExist:
                return Response({'detail': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
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
        
class GetChatLTEView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
                chat_not_read=0
                alert_not_read=0
                update_not_read=0
                approve_not_read=0
                member_updated_not_check=0
                qs_user_chatroom=AppChatRoom.objects.filter(members=qs_staff)
                for qs_chatroom in qs_user_chatroom:
                    qs_last_read=AppChatStatus.objects.filter(room=qs_chatroom,user=qs_staff).first()
                    if qs_last_read and qs_last_read.last_read_at:
                        qs_not_read=ChatMessage.objects.filter(room=qs_chatroom,created_at__gt=qs_last_read.last_read_at)
                        chat_not_read+=qs_not_read.count()
                    else:
                        qs_not_read=ChatMessage.objects.filter(room=qs_chatroom)
                        chat_not_read+=qs_not_read.count()
                last_check=LastCheckAPI.objects.filter(user=qs_staff)
                return Response({
                    'chats': AppChatRoomSerializer(AppChatRoom.objects.filter(members=qs_staff),many=True).data,
                    'chat_not_read': chat_not_read,
                    'alert_not_read': alert_not_read,
                    'update_not_read': update_not_read,
                    'approve_not_read': approve_not_read,
                    'member_updated_not_check': member_updated_not_check,
                    'last_check':LastCheckAPISerializer(last_check,many=True).data
                }, status=status.HTTP_200_OK)
            except CompanyStaff.DoesNotExist:
                return Response({'detail': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
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
        
class GetUserAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
                qs_profile,_=CompanyStaffProfile.objects.get_or_create(staff=qs_staff)
                chat_not_read=0
                alert_not_read=0
                update_not_read=0
                approve_not_read=0
                member_updated_not_check=0
                qs_user_chatroom=AppChatRoom.objects.filter(members=qs_staff)
                for qs_chatroom in qs_user_chatroom:
                    qs_last_read=AppChatStatus.objects.filter(room=qs_chatroom,user=qs_staff).first()
                    if qs_last_read and qs_last_read.last_read_at:
                        qs_not_read=ChatMessage.objects.filter(room=qs_chatroom,created_at__gt=qs_last_read.last_read_at)
                        chat_not_read+=qs_not_read.count()
                    else:
                        qs_not_read=ChatMessage.objects.filter(room=qs_chatroom)
                        chat_not_read+=qs_not_read.count()
                last_check=LastCheckAPI.objects.filter(user=qs_staff)
                return Response({
                    'id': qs_staff.id,
                    'info': CompanyStaffSerializer(qs_staff).data,
                    'company': CompanySerializer(qs_staff.company).data,
                    'chatbox': AppChatRoomSerializer(AppChatRoom.objects.filter(members=qs_staff),many=True).data,
                    'app_config': {
                        'chat_not_read': chat_not_read,
                        'alert_not_read': alert_not_read,
                        'update_not_read': update_not_read,
                        'approve_not_read': approve_not_read,
                        'member_updated_not_check': member_updated_not_check,
                        'last_check':LastCheckAPISerializer(last_check,many=True).data
                    }
                }, status=status.HTTP_200_OK)
            except CompanyStaff.DoesNotExist:
                return Response({'detail': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
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
        
    def post(self, request):
        user=request.user
        key = request.headers.get('ApplicationKey')
        qs_user_company=CompanyStaff.objects.get(user__user=user,company__key=key)
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            cardID = request.data.get('cardID',None)
            department = request.data.get('department')
            possition = request.data.get('possition')
            role = request.data.get('role')
            fullname = request.data.get('fullname')
            birthday = request.data.get('birthday')
            managerCustomer = request.data.get('managerCustomer')
            isAdmin=False
            isSuper=False
            if role=="Admin":
                if qs_user_company.isAdmin==False:
                    return Response(
                        data={"detail":"Bạn không có quyền tạo tài khoản admin!"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                isAdmin=True
            if role=="SuperAdmin":
                if qs_user_company.isSuperAdmin==False:
                    return Response(
                        data={"detail":"Bạn không có quyền tạo tài khoản boss!"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                isAdmin=True
                isSuper=True
            qs_user=CompanyUser.objects.filter(username=username)
            last_id = CompanyStaff.objects.filter(company__key=key).count()
            company_code=qs_user_company.company.companyCode
            if not cardID:
                if not company_code:
                    company_code="MNV"
                count = f"{last_id:06d}"
                cardID=f"{company_code}-{count}"
            if qs_user_company.isAdmin or qs_user_company.isSuperAdmin:
                if not qs_user:
                    with transaction.atomic():
                        new_user=User.objects.create(username=f"{key}_{username}",password=uuid.uuid4().hex.upper())
                        new_company_user=CompanyUser.objects.create(user=new_user,
                                                                    username=username,
                                                                    password=password,
                                                                    company=qs_user_company.company)
                        qs_department=None
                        qs_possition=None
                        if department:
                            qs_department,_=CompanyDepartment.objects.get_or_create(
                                name=department,
                                company=qs_user_company.company,
                                isActive=True)
                        if possition:
                            qs_possition,_=CompanyPossition.objects.get_or_create(
                                name=possition,
                                department=qs_department,
                                company=qs_user_company.company,
                                isActive=True
                            )
                        staff=CompanyStaff.objects.create(company=qs_user_company.company,
                                                        cardID=cardID,
                                                        department=qs_department,
                                                        possition=qs_possition,
                                                        user=new_company_user,
                                                        isActive=True,
                                                        isSuperAdmin=isSuper,
                                                        created_by=qs_user_company,
                                                        isAdmin=isAdmin)
                        if managerCustomer:
                            for cus in managerCustomer:
                                qs_cus=CompanyCustomer.objects.get(id=cus)
                                staff.managerCustomer.add(qs_cus)
                                staff.save()
                        profile=CompanyStaffProfile.objects.create(
                            staff=staff,
                            full_name=fullname if fullname else cardID,
                            date_of_birth=birthday
                        )
                        return Response(data=CompanyStaffDetailsSerializer(staff).data, status=status.HTTP_201_CREATED)
                else:
                    return Response(data={"detail":"Tên tài khoản này đã được sử dụng!"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data={"detail":"Bạn không có quyền tạo tài khoản mới!"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data={"detail":"Bạn không có quyền tạo tài khoản mới!","error":res_data}, status=status.HTTP_400_BAD_REQUEST)
        
class GetUserSocketAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
                qs_profile=None
                try:
                    qs_profile=CompanyStaffProfile.objects.get(staff=qs_staff)
                except:
                    pass
                return Response({
                    'id': qs_staff.id,
                    'info': CompanyStaffSerializer(qs_staff).data,
                    'company': CompanySerializer(qs_staff.company).data
                }, status=status.HTTP_200_OK)
            except CompanyStaff.DoesNotExist:
                return Response({'detail': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'detail': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)
        