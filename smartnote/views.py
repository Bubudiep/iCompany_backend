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

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50  # Số lượng đối tượng trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 200  # Số lượng đối tượng tối đa trên mỗi trang

class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = NoteUser.objects.get(oauth_user=request.user)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
class NoteUserRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = NoteUserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            note_user = serializer.save()
            return Response({
                "message": "NoteUser created successfully",
                "data":UserSerializer(note_user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class NoteUserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        try:
            note_user = NoteUser.objects.get(username=username)
            oauth_user = note_user.oauth_user
        except NoteUser.DoesNotExist:
            return Response({"detail": "Tài khoản chưa được đăng ký!"}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=oauth_user.username, password=password)
        if not user:
            return Response({"detail": "Mật khẩu không chính xác!"}, status=status.HTTP_400_BAD_REQUEST)
        # Tạo access token thủ công (nếu không dùng password grant)
        app = Application.objects.filter(user=oauth_user).first()
        if not app:
            app = Application.objects.create(
                user=oauth_user,
                client_type=Application.CLIENT_CONFIDENTIAL,
                authorization_grant_type=Application.GRANT_PASSWORD,
                name="SmartNote App",
            )
        expires = timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        access_token = AccessToken.objects.create(
            user=oauth_user,
            application=app,
            expires=expires,
            token=secrets.token_urlsafe(32),
            scope="read write"
        )
        return Response({
            "access_token": access_token.token,
            "expires_in": oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            "token_type": "Bearer",
        })
        
class UserNotesViewSet(viewsets.ModelViewSet):
    queryset = UserNotes.objects.all().order_by("-created_at")
    serializer_class = UserNotesSerializer
    def perform_create(self, serializer):
        user_id = self.request.data.get("user_id")
        try:
            note_user = NoteUser.objects.get(id=user_id)
        except NoteUser.DoesNotExist:
            raise serializers.ValidationError("NoteUser không tồn tại.")
        serializer.save(user=note_user)
    @action(detail=True, methods=["post"])
    def share(self, request, pk=None):
        note = self.get_object()
        shared_with_id = request.data.get("shared_with_id")
        can_edit = request.data.get("can_edit", False)
        try:
            target_user = NoteUser.objects.get(id=shared_with_id)
        except NoteUser.DoesNotExist:
            return Response({"error": "Người nhận không tồn tại"}, status=400)

        if note.user == target_user:
            return Response({"error": "Không thể chia sẻ với chính mình"}, status=400)
        shared, created = SharedNote.objects.get_or_create(
            note=note,
            shared_with=target_user,
            defaults={"can_edit": can_edit}
        )
        if not created:
            shared.can_edit = can_edit
            shared.save()

        return Response({"message": "Đã chia sẻ ghi chú"}, status=200)
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