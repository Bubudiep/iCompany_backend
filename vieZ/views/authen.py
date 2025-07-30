from .a import *

class MyInfo(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def get(self, request):
        key = request.headers.get('ApplicationKey')
        
        if request.user.is_authenticated:
            user=request.user
            return Response(UserSerializer(user).data)
        else:
            return Response({'detail': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)
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
            user=User.objects.get(username=f"{key}_{username}")
            user.last_login=now()
            user.save()
            if check_password(password, user.password)==False:
                    return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
            token = generate_token()
            access_token = AccessToken.objects.create(
                user=user,
                token=token,
                application=application,
                expires=now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
                scope='read write'
            )
            refresh_token_instance = RefreshToken.objects.create(
                user=user,
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
        except User.DoesNotExist:
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
           
  