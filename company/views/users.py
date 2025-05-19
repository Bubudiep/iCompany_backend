from .a import *

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Nếu muốn chỉ cho xem/cập nhật profile của chính mình
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    def perform_update(self, serializer):
        serializer.save()  # Bạn có thể gắn thêm logic ở đây nếu muốn log cập nhật

        
class CompanyStaffProfileViewSet(viewsets.ModelViewSet):
    queryset = CompanyStaffProfile.objects.all()
    serializer_class = CompanyStaffProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Nếu muốn chỉ cho xem/cập nhật profile của chính mình
    def get_queryset(self):
        return CompanyStaffProfile.objects.filter(staff__user=self.request.user)
    def perform_update(self, serializer):
        serializer.save()  # Bạn có thể gắn thêm logic ở đây nếu muốn log cập nhật