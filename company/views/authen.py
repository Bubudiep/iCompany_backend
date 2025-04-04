from .a import *

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
            print(f"{ip}")
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
            return Response({
                'access_token': token,
                'refresh_token': refresh_token_instance.token,
                'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                'token_type': 'Bearer',
                'scope': access_token.scope,
                'user': CompanyStaffSerializer(staff).data
            }, status=status.HTTP_200_OK)
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
        key = request.headers.get('ApplicationKey')
        if request.user.is_authenticated:
            user=request.user
            try:
                qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
                qs_profile=None
                try:
                    qs_profile=UserProfile.objects.get(user=user)
                except:
                    pass
                chat_not_read=0
                alert_not_read=0
                update_not_read=0
                approve_not_read=0
                member_updated_not_check=0
                qs_user_chatroom=AppChatRoom.objects.filter(members=qs_staff)
                for qs_chatroom in qs_user_chatroom:
                    qs_last_read=AppChatStatus.objects.filter(room=qs_chatroom,user=qs_staff).first()
                    if qs_last_read:
                        qs_not_read=ChatMessage.objects.filter(room=qs_chatroom,created_at__gt=qs_last_read.last_read_at)
                        chat_not_read+=qs_not_read.count()
                    else:
                        qs_not_read=ChatMessage.objects.filter(room=qs_chatroom)
                        chat_not_read+=qs_not_read.count()
                        
                return Response({
                    'id': qs_staff.id,
                    'staff': CompanyStaffSerializer(
                        CompanyStaff.objects.filter(
                            company__key=key,
                            isActive=True,
                            isBan=False
                        ),many=True
                    ).data,
                    'company': CompanySerializer(qs_staff.company).data,
                    'profile': UserProfileSerializer(qs_profile).data if qs_profile else None,
                    'app_list': [],
                    'app_config': {
                        'chat_not_read': chat_not_read,
                        'alert_not_read': alert_not_read,
                        'update_not_read': update_not_read,
                        'approve_not_read': approve_not_read,
                        'member_updated_not_check': member_updated_not_check
                    }
                }, status=status.HTTP_200_OK)
            except CompanyStaff.DoesNotExist:
                return Response({'detail': "Bạn không có quyền truy cập!"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'detail': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)
        