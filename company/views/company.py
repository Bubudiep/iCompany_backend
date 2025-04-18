from .a import *

class CompanyAccountsViewSet(viewsets.ModelViewSet):
    queryset =CompanyStaff.objects.all()
    serializer_class =CompanyStaffSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'post']
    pagination_class = StandardResultsSetPagination
    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        user = request.user
        key = request.headers.get('ApplicationKey')
        try:
            current_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        if not (current_staff.isAdmin or current_staff.isSuperAdmin):
            return Response({"detail": "Bạn không có quyền reset mật khẩu"}, status=status.HTTP_403_FORBIDDEN)
        account = self.get_object()
        if account.isSuperAdmin:
            return Response({"detail": "Không thể reset mật khẩu SuperAdmin"}, status=status.HTTP_403_FORBIDDEN)
        if account.isAdmin and not current_staff.isSuperAdmin:
            return Response({"detail": "Không thể reset mật khẩu Admin khác"}, status=status.HTTP_403_FORBIDDEN)
        new_password = get_random_string(length=10)
        account.user.password=new_password
        account.user.save()
        return Response({
            "detail": "Mật khẩu đã được reset.",
            "new_password": new_password
        }, status=status.HTTP_200_OK)
        
    def create(self, request, *args, **kwargs):
        return Response({"detail": "Bạn không được phép tạo tài khoản mới"}, status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        key = self.request.headers.get('ApplicationKey')
        user = self.request.user
        qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
        return CompanyStaff.objects.filter(company__key=qs_staff.company.key)
        
    def partial_update(self, request, *args, **kwargs):
        user = request.user
        key = request.headers.get('ApplicationKey')
        account=self.get_object()
        try:
            qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không tồn tại trong công ty này"}, status=status.HTTP_403_FORBIDDEN)

        if not (qs_staff.isAdmin or qs_staff.isSuperAdmin):
            return Response({"detail": "Bạn không có quyền cập nhật thông tin nhân viên"}, status=status.HTTP_403_FORBIDDEN)
        if account.isSuperAdmin:
            return Response({"detail": "Bạn không có quyền cập nhật thông tin nhân viên này"}, status=status.HTTP_403_FORBIDDEN)
        if account.isAdmin:
            if qs_staff.isAdmin:
              return Response({"detail": "Bạn không có quyền cập nhật thông tin nhân viên này"}, status=status.HTTP_403_FORBIDDEN)
        if request.data.get("cardID"):
            qs_staff = CompanyStaff.objects.filter(cardID=request.data.get("cardID")).exclude(user__user=user)
            if len(qs_staff):
              return Response({"detail": "Mã nhân viên đã tồn tại!"}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
    def list(self, request, *args, **kwargs):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
        if qs_staff.isAdmin==False:
          return Response({"detail":"Bạn không có quyền truy cập"},status=status.HTTP_400_BAD_REQUEST)
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