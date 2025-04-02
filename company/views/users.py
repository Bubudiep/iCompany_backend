from rest_framework import viewsets, permissions
from ..models import *
from ..serializers import *

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Nếu muốn chỉ cho xem/cập nhật profile của chính mình
    def get_queryset(self):
        # Chỉ trả về profile của người dùng hiện tại
        return UserProfile.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()  # Bạn có thể gắn thêm logic ở đây nếu muốn log cập nhật
