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


class CompanyCustomerViewSet(viewsets.ModelViewSet):
    queryset = CompanyCustomer.objects.all()
    serializer_class = CompanyCustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'post']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        key = self.request.headers.get('ApplicationKey')
        user = self.request.user
        qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
        return CompanyCustomer.objects.filter(company__key=qs_staff.company.key)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class CompanyVendorViewSet(viewsets.ModelViewSet):
    queryset = CompanyVendor.objects.all()
    serializer_class = CompanyVendorSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'post']
    pagination_class = StandardResultsSetPagination
    
    @action(detail=False, methods=['get'], url_path='download_template')
    def download_template(self, request):
        df = pd.DataFrame(columns=["name", "fullname", "email", "hotline", "address", "website"])
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="vendor_template.xlsx"'
        return response
    
    @action(detail=False, methods=['post'], url_path='upload_excel')
    def upload_excel(self, request):
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "No file uploaded."}, status=400)
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            return Response({"error": f"Invalid Excel file: {str(e)}"}, status=400)
        required_columns = ['name', 'fullname', 'email', 'hotline', 'address', 'website']
        for col in required_columns:
            if col not in df.columns:
                return Response({"error": f"Missing column: {col}"}, status=400)
        key = request.headers.get('ApplicationKey')
        user = request.user
        qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        created_count = 0
        for _, row in df.iterrows():
            if pd.isna(row["name"]):
                continue
            vendor_data = {
                "company": qs_staff.company,
                "name": row["name"],
                "fullname": row.get("fullname", ""),
                "email": row.get("email", ""),
                "hotline": row.get("hotline", ""),
                "address": row.get("address", ""),
                "website": row.get("website", ""),
            }
            CompanyVendor.objects.update_or_create(
                company=qs_staff.company,
                name=row["name"],
                defaults=vendor_data
            )
            created_count += 1
        return Response({"message": f"Imported {created_count} vendors."}, status=200)
    
    def perform_create(self, serializer):
        key = self.request.headers.get('ApplicationKey')
        user = self.request.user
        qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        serializer.save(company=qs_staff.company)

    def get_queryset(self):
        key = self.request.headers.get('ApplicationKey')
        user = self.request.user
        qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
        return CompanyVendor.objects.filter(company__key=qs_staff.company.key)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)