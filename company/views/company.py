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
        qs_staff=update_lastcheck(self,'Account')
        return CompanyStaff.objects.filter(company__key=qs_staff.company.key)
        
    def partial_update(self, request, *args, **kwargs):
        user = request.user
        key = request.headers.get('ApplicationKey')
        account=self.get_object()
        try:
            qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không tồn tại trong công ty này"}, status=status.HTTP_403_FORBIDDEN)
        if qs_staff!=account:
            if not (qs_staff.isAdmin or qs_staff.isSuperAdmin):
                return Response({"detail": "Bạn không phải admin/boss"}, status=status.HTTP_403_FORBIDDEN)
            if account.isSuperAdmin:
                if qs_staff.isSuperAdmin==False:
                    return Response({"detail": "Bạn không có quyền cập nhật thông tin Boss"}, status=status.HTTP_403_FORBIDDEN)
            if account.isAdmin:
                if qs_staff.isSuperAdmin==False:
                    return Response({"detail": "Bạn không có quyền cập nhật thông tin nhân viên này"}, status=status.HTTP_403_FORBIDDEN)
            if request.data.get("cardID"):
                qs_staff = CompanyStaff.objects.filter(cardID=request.data.get("cardID")).exclude(id=account.id)
                if len(qs_staff)>0:
                    return Response({"detail": "Mã nhân viên đã tồn tại!"}, status=status.HTTP_403_FORBIDDEN)
        
        if request.data.get("department"):
            qs_department,_=CompanyDepartment.objects.get_or_create(name=request.data.get("department"),company=qs_staff.company)
            request.data["department"]=qs_department.id
            if qs_department and request.data.get("possition"):
                qs_department.updated_at=now
                qs_department.save()
                qs_pos,_=CompanyPossition.objects.get_or_create(name=request.data.get("possition"),isActive=True,department=qs_department,company=qs_staff.company)
                print(f"{qs_pos}")
                request.data["possition"]=qs_pos.id
        return super().partial_update(request, *args, **kwargs)
    def list(self, request, *args, **kwargs):
        qs_staff=update_lastcheck(self,'Account')
        if qs_staff.isSuperAdmin==False:
            if qs_staff.isAdmin==False:
                return Response({"detail":"Bạn không có quyền truy cập"},status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        last_update = self.request.query_params.get('last_update')
        if last_update:
            queryset=queryset.filter(updated_at__gt=last_update)
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
    
    @action(detail=False, methods=['post'])
    def multi_create(self, request, pk=None):
        user = request.user
        key = request.headers.get('ApplicationKey')
        try:
            staff = CompanyStaff.objects.get(user__user=user, company__key=key)
            data=request.data.get('data')
            if not data or not isinstance(data, list):
                return Response({"detail": "Dữ liệu không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
            if data:
                with transaction.atomic():
                    for cus in data:
                        print(f"{cus.get('name')}")
                        qs_old=CompanyVendor.objects.filter(
                            company=staff.company,name=cus.get('name')
                        )
                        if len(qs_old)==0:
                            serializer= self.get_serializer(data=cus)
                            if serializer.is_valid():
                                serializer.save(company=staff.company)
                return Response(CompanyVendorSerializer(CompanyVendor.objects.filter(company=staff.company),many=True).data, status=status.HTTP_200_OK)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "detail": "Không thể cập nhập"
        }, status=status.HTTP_403_FORBIDDEN)
        
    def create(self, request, *args, **kwargs):
        key = self.request.headers.get('ApplicationKey')
        qs_ven=CompanyVendor.objects.filter(company__key=key,name=request.data.get('name'))
        print(f"{qs_ven}")
        if len(qs_ven)>0:
            return Response({"detail": "Tên nhà cung cấp đã tồn tại"}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        key = self.request.headers.get('ApplicationKey')
        user = self.request.user
        qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        serializer.save(company=qs_staff.company)

    def get_queryset(self):
        qs_staff=update_lastcheck(self,'Vendor')
        return CompanyVendor.objects.filter(company__key=qs_staff.company.key)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        last_update = self.request.query_params.get('last_update')
        if last_update:
            queryset=queryset.filter(updated_at__gt=last_update)
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

    @action(detail=False, methods=['post'])
    def multi_create(self, request, pk=None):
        user = request.user
        key = request.headers.get('ApplicationKey')
        try:
            staff = CompanyStaff.objects.get(user__user=user, company__key=key)
            data=request.data.get('data')
            if not data or not isinstance(data, list):
                return Response({"detail": "Dữ liệu không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
            if data:
                with transaction.atomic():
                    for cus in data:
                        print(f"{cus.get('name')}")
                        qs_old=CompanyCustomer.objects.filter(
                            company=staff.company,name=cus.get('name')
                        )
                        if len(qs_old)==0:
                            serializer= self.get_serializer(data=cus)
                            if serializer.is_valid():
                                serializer.save(company=staff.company)
                return Response(CompanyCustomerSerializer(CompanyCustomer.objects.filter(company=staff.company),many=True).data, status=status.HTTP_200_OK)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "detail": "Không thể cập nhập"
        }, status=status.HTTP_403_FORBIDDEN)
        
    def create(self, request, *args, **kwargs):
        key = self.request.headers.get('ApplicationKey')
        qs_ven=CompanyCustomer.objects.filter(company__key=key,name=request.data.get('name'))
        if len(qs_ven)>0:
            return Response({"detail": "Khách hàng này đã tồn tại"}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        key = self.request.headers.get('ApplicationKey')
        user = self.request.user
        qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        serializer.save(company=qs_staff.company)

    def get_queryset(self):
        qs_staff=update_lastcheck(self,'Customer')
        return CompanyCustomer.objects.filter(company__key=qs_staff.company.key)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        last_update = self.request.query_params.get('last_update')
        if last_update:
            queryset=queryset.filter(updated_at__gt=last_update)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CompanyDepartmentViewSet(viewsets.ModelViewSet):
    queryset = CompanyDepartment.objects.all()
    serializer_class = CompanyDepartmentDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'post']
    pagination_class = StandardResultsSetPagination
    
    def perform_create(self, serializer):
        key = self.request.headers.get('ApplicationKey')
        user = self.request.user
        qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        serializer.save(company=qs_staff.company)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CompanyDepartmentDetailsSerializer(instance)
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        user = request.user
        key = request.headers.get('ApplicationKey')
        try:
            qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không tồn tại trong công ty này"}, status=status.HTTP_403_FORBIDDEN)

        if not qs_staff.isSuperAdmin:
            return Response({"detail": "Bạn không có quyền cập nhật thông tin này"}, status=status.HTTP_403_FORBIDDEN)
        response = super().partial_update(request, *args, **kwargs)
        instance = self.get_object()
        serializer = CompanyDepartmentDetailsSerializer(instance, context={'request': request})
        return Response(serializer.data)
    
    def get_queryset(self):
        qs_staff=update_lastcheck(self,'Department')
        return CompanyDepartment.objects.filter(company__key=qs_staff.company.key)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        last_update = self.request.query_params.get('last_update')
        if last_update:
            queryset=queryset.filter(updated_at__gt=last_update)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class CompanyPossitionViewSet(viewsets.ModelViewSet):
    queryset = CompanyPossition.objects.all()
    serializer_class = CompanyPossitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'post']
    pagination_class = StandardResultsSetPagination
    
    def perform_create(self, serializer):
        key = self.request.headers.get('ApplicationKey')
        user = self.request.user
        qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        serializer.save(company=qs_staff.company)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CompanyPossitionDetailsSerializer(instance)
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        user = request.user
        key = request.headers.get('ApplicationKey')
        try:
            qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không tồn tại trong công ty này"}, status=status.HTTP_403_FORBIDDEN)

        if not qs_staff.isSuperAdmin:
            return Response({"detail": "Bạn không có quyền cập nhật thông tin này"}, status=status.HTTP_403_FORBIDDEN)
        response = super().partial_update(request, *args, **kwargs)
        instance = self.get_object()
        serializer = CompanyPossitionDetailsSerializer(instance, context={'request': request})
        return Response(serializer.data)
    
    def get_queryset(self):
        qs_staff=update_lastcheck(self,"Possition")
        return CompanyPossition.objects.filter(company__key=qs_staff.company.key)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        last_update = self.request.query_params.get('last_update')
        if last_update:
            queryset=queryset.filter(updated_at__gt=last_update)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class CompanyStaffProfileViewSet(viewsets.ModelViewSet):
    queryset = CompanyStaffProfile.objects.all()
    serializer_class = CompanyStaffProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch','post']
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        staff=CompanyStaff.objects.get(company__key=key,user__user=user)
        return CompanyStaffProfile.objects.filter(staff=staff)
    
    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Không được phép'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def change_pass(self, request, pk=None):
        user = request.user
        key = request.headers.get('ApplicationKey')
        old_pass = request.data.get("old_pass")
        new_pass = request.data.get("new_pass")
        try:
            staff = CompanyStaff.objects.get(user__user=user, company__key=key)
            cuser = staff.user
            if check_password(old_pass, cuser.password)==False:
                return Response({'detail': 'Sai mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                cuser.password=new_pass
                cuser.save()
            return Response({"detail": "Thành công!"}, status=status.HTTP_200_OK)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        last_update = self.request.query_params.get('last_update')
        if last_update:
            queryset=queryset.filter(updated_at__gt=last_update)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class AdvanceRequestViewSet(viewsets.ModelViewSet):
    queryset = AdvanceRequest.objects.all()
    serializer_class = AdvanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get','post']
    pagination_class = StandardResultsSetPagination
    lookup_field = 'request_code'

    @action(detail=True, methods=['post'])
    def paytrieve(self, request, request_code=None):
        user = request.user
        key = request.headers.get('ApplicationKey')
        apv = self.get_object()
        try:
            staff = CompanyStaff.objects.get(user__user=user, company__key=key)
            config,_ = CompanyConfig.objects.get_or_create(company=staff.company)
            if staff in config.staff_can_payout.all():
                pass  # Được phép
            elif staff.isSuperAdmin:
                pass  # Super admin luôn được phép
            elif staff.isAdmin and config.admin_can_payout:
                pass  # Admin được phép nếu config cho phép
            else:
                return Response({"detail": "Bạn không có quyền hoàn ngân",
                                 "reason": "Không thuộc nhóm hoàn ngân và không phải admin/super admin"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            if apv.status!="approved":
                return Response({"detail": "Chưa được phê duyệt"}, status=status.HTTP_403_FORBIDDEN)
            if apv.payment_status!="done":
                return Response({"detail": "Chưa được giải ngân"}, status=status.HTTP_403_FORBIDDEN)
            apv.retrieve_status="done"
            apv.save()
            AdvanceRequestHistory.objects.create(request=apv,
                user=staff,
                action='retrieve',
                comment=request.data.get('comment')
            )
            if apv.operator:
                OperatorUpdateHistory.objects.create(
                    operator=apv.operator,
                    changed_by=staff,
                    notes=f"Thu hồi {apv.amount} từ phê duyệt [approve|{apv.request_code}]"
                )
            return Response(AdvanceRequestSerializer(apv).data, status=status.HTTP_200_OK)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "detail": "Không thể cập nhập"
        }, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=True, methods=['post'])
    def payout(self, request, request_code=None):
        user = request.user
        key = request.headers.get('ApplicationKey')
        apv = self.get_object()
        try:
            staff = CompanyStaff.objects.get(user__user=user, company__key=key)
            config,_ = CompanyConfig.objects.get_or_create(company=staff.company)
            if apv.status!="approved":
                return Response({"detail": "Chưa được phê duyệt"}, status=status.HTTP_403_FORBIDDEN)
            if apv.payment_status=="done":
                return Response({"detail": "Đã giải ngân trước đó"}, status=status.HTTP_403_FORBIDDEN)
            if staff in config.staff_can_payout.all():
                pass  # Được phép
            elif staff.isSuperAdmin:
                pass  # Super admin luôn được phép
            elif staff.isAdmin and config.admin_can_payout:
                pass  # Admin được phép nếu config cho phép
            else:
                return Response({"detail": "Bạn không có quyền giải ngân",
                                 "reason": "Không thuộc nhóm giải ngân và không phải admin/super admin"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            apv.payout_amount=apv.amount
            apv.payment_status="done"
            apv.save()
            AdvanceRequestHistory.objects.create(request=apv,
                user=staff,
                action='payout',
                comment=request.data.get('comment')
            )
            if apv.operator:
                OperatorUpdateHistory.objects.create(
                    operator=apv.operator,
                    changed_by=staff,
                    notes=f"Giải ngân {apv.amount} từ phê duyệt [approve|{apv.request_code}]"
                )
            return Response(AdvanceRequestSerializer(apv).data, status=status.HTTP_200_OK)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "detail": "Không thể cập nhập"
        }, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=True, methods=['post'])
    def update_amount(self, request, request_code=None):
        user = request.user
        key = request.headers.get('ApplicationKey')
        apv = self.get_object()
        try:
            staff = CompanyStaff.objects.get(user__user=user, company__key=key)
            config,_ = CompanyConfig.objects.get_or_create(company=staff.company)
            if staff.isSuperAdmin:
                pass
            elif staff.isAdmin:
                pass
            elif staff in config.staff_approve_admin.all():
                pass  # Được phép phê duyệt
            elif staff != apv.requester:
                return Response({"detail": "Bạn không có quyền hủy",
                                 "reason": "Không phải người tạo yêu cầu hoặc super admin"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            n_amount=request.data.get('amount',None)
            o_amount=apv.amount
            if n_amount:
                if apv.payment_status=="done":
                    apv.payout_amount=n_amount
                apv.amount=n_amount
                apv.save()
                AdvanceRequestHistory.objects.create(request=apv,
                    user=staff,
                    action='update',
                    comment=f'update số tiền: {o_amount} -> {n_amount}'
                )
            return Response(AdvanceRequestSerializer(apv).data, status=status.HTTP_200_OK)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "detail": "Không thể cập nhập"
        }, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=True, methods=['post'])
    def cancel(self, request, request_code=None):
        user = request.user
        key = request.headers.get('ApplicationKey')
        apv = self.get_object()
        try:
            staff = CompanyStaff.objects.get(user__user=user, company__key=key)
            config,_ = CompanyConfig.objects.get_or_create(company=staff.company)
            if apv.status not in ["pending"]:
                return Response({"detail": "Trạng thái không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
            if staff.isSuperAdmin:
                pass
            elif staff in config.staff_approve_admin.all():
                pass  # Được phép phê duyệt
            elif staff != apv.requester:
                return Response({"detail": "Bạn không có quyền hủy",
                                 "reason": "Không phải người tạo yêu cầu hoặc super admin"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            apv.status="cancel"
            apv.save()
            AdvanceRequestHistory.objects.create(request=apv,
                user=staff,
                action='cancel',
                comment=request.data.get('comment')
            )
            if apv.operator:
                OperatorUpdateHistory.objects.create(
                    operator=apv.operator,
                    changed_by=staff,
                    notes=f"Hủy yêu cầu {apv.amount} từ phê duyệt [approve|{apv.request_code}]"
                )
            return Response(AdvanceRequestSerializer(apv).data, status=status.HTTP_200_OK)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "detail": "Không thể cập nhập"
        }, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=True, methods=['post'])
    def reject(self, request, request_code=None):
        user = request.user
        key = request.headers.get('ApplicationKey')
        apv = self.get_object()
        try:
            if apv.status not in ["pending"]:
                return Response({"detail": "Trạng thái không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
            staff = CompanyStaff.objects.get(user__user=user, company__key=key)
            config,_ = CompanyConfig.objects.get_or_create(company=staff.company)
            if staff in config.staff_approve_admin.all():
                pass  # Được phép phê duyệt
            if staff in config.staff_can_approve.all():
                pass  # Được phép phê duyệt
            elif staff.isSuperAdmin:
                pass  # Super admin luôn được phép
            elif staff.isAdmin and config.admin_can_approve:
                pass  # Admin được phép nếu config cho phép
            else:
                return Response({"detail": "Bạn không có quyền phê duyệt",
                                 "reason": "Không thuộc nhóm phê duyệt và không phải admin/super admin"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            apv.status="rejected"
            apv.save()
            AdvanceRequestHistory.objects.create(request=apv,
                user=staff,
                action='rejected',
                comment=request.data.get('comment')
            )
            if apv.operator:
                OperatorUpdateHistory.objects.create(
                    operator=apv.operator,
                    changed_by=staff,
                    notes=f"Từ chối phê duyệt [approve|{apv.request_code}]"
                )
            return Response(AdvanceRequestSerializer(apv).data, status=status.HTTP_200_OK)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "detail": "Không thể cập nhập"
        }, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=True, methods=['post'])
    def apply_pay(self, request, request_code=None):
        user = request.user
        key = request.headers.get('ApplicationKey')
        apv = self.get_object()
        if apv.status not in ["approved","pending"]:
            return Response({"detail": "Trạng thái không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        if apv.payment_status=="done":
            return Response({"detail": "Đã giải ngân trước đó"}, status=status.HTTP_403_FORBIDDEN)
        try:
            staff = CompanyStaff.objects.get(user__user=user, company__key=key)
            config,_ = CompanyConfig.objects.get_or_create(company=staff.company)
            if staff in config.staff_approve_admin.all():
                pass  # Được phép phê duyệt
            if staff in config.staff_can_approve.all() and staff in config.staff_can_payout.all():
                pass  # Được phép phê duyệt
            elif staff.isSuperAdmin:
                pass  # Super admin luôn được phép
            elif staff.isAdmin and config.admin_can_approve and config.staff_can_payout:
                pass  # Admin được phép nếu config cho phép
            else:
                return Response({"detail": "Bạn không có quyền phê duyệt",
                                 "reason": "Không thuộc nhóm phê duyệt và không phải admin/super admin"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            apv.status="approved"
            apv.payment_status="done"
            apv.payout_amount=apv.amount
            apv.save()
            AdvanceRequestHistory.objects.create(request=apv,
                user=staff,
                action='approved',
                comment=request.data.get('comment')
            )
            AdvanceRequestHistory.objects.create(request=apv,
                user=staff,
                action='payout',
                comment=request.data.get('comment')
            )
            if apv.operator:
                OperatorUpdateHistory.objects.create(
                    operator=apv.operator,
                    changed_by=staff,
                    notes=f"Chấp nhận và giải ngân phê duyệt [approve|{apv.request_code}]"
                )
            return Response(AdvanceRequestSerializer(apv).data, status=status.HTTP_200_OK)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data={"detail":"Bạn không có quyền tạo tài khoản mới!","error":res_data}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "detail": "Không thể cập nhập"
        }, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=True, methods=['post'])
    def apply(self, request, request_code=None):
        try:
            user = request.user
            key = request.headers.get('ApplicationKey')
            apv = self.get_object()
            staff = CompanyStaff.objects.get(user__user=user, company__key=key)
            config,_ = CompanyConfig.objects.get_or_create(company=staff.company)
            if apv.status not in ["pending"] and apv.payment_status!="not":
                return Response({"detail": "Trạng thái không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
            if staff in config.staff_approve_admin.all():
                pass  # Được phép phê duyệt
            if staff in config.staff_can_approve.all():
                pass  # Được phép phê duyệt
            elif staff.isSuperAdmin:
                pass  # Super admin luôn được phép
            elif staff.isAdmin and config.admin_can_approve:
                pass  # Admin được phép nếu config cho phép
            else:
                return Response({"detail": "Bạn không có quyền phê duyệt",
                                 "reason": "Không thuộc nhóm phê duyệt và không phải admin/super admin"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            apv.status="approved"
            apv.save()
            AdvanceRequestHistory.objects.create(request=apv,
                user=staff,
                action='approved',
                comment=request.data.get('comment')
            )
            if apv.operator:
                OperatorUpdateHistory.objects.create(
                    operator=apv.operator,
                    changed_by=staff,
                    notes=f"Chấp nhận yêu cầu phê duyệt [approve|{apv.request_code}]"
                )
            return Response(AdvanceRequestSerializer(apv).data, status=status.HTTP_200_OK)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            res_data = generate_response_json("FAIL", f"[{file_name}_{lineno}] {str(e)}")
            return Response(data={"detail":"Bạn không có quyền tạo tài khoản mới!","error":res_data}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "detail": "Không thể cập nhập"
        }, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AdvanceRequestDetailsSerializer(instance)
        return Response(serializer.data)
        
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        staff=CompanyStaff.objects.get(company__key=key,user__user=user)
        return AdvanceRequest.objects.filter(company=staff.company)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        created_at = request.query_params.get('created_at')
        created_at_from = request.query_params.get('created_at_from')
        created_at_to = request.query_params.get('created_at_to')
        if created_at_from:
            try:
                date_from = make_aware(datetime.combine(parse_date(created_at_from), datetime.min.time()))
                queryset = queryset.filter(created_at__gte=date_from)
            except:
                pass
        if created_at_to:
            try:
                date_to = make_aware(datetime.combine(parse_date(created_at_to), datetime.max.time()))
                queryset = queryset.filter(created_at__lte=date_to)
            except:
                pass
        if created_at:
            try:
                date = make_aware(datetime.combine(parse_date(created_at), datetime.min.time()))
                next_day = make_aware(datetime.combine(parse_date(created_at), datetime.max.time()))
                queryset = queryset.filter(created_at__range=(date, next_day))
            except:
                pass
        staff = self.request.query_params.get('staff')
        if staff:
            queryset=queryset.filter(requester__id=int(staff))
        qs_bankType = self.request.query_params.get('banktype')
        if qs_bankType:
            queryset=queryset.filter(hinhthucThanhtoan=qs_bankType)
        qs_operator = self.request.query_params.get('operator')
        if qs_operator:
            queryset=queryset.filter(operator__id=qs_operator)
        qs_request_code = self.request.query_params.get('request_code')
        if qs_request_code:
            queryset=queryset.filter(request_code__contains=qs_request_code)
        qs_type = self.request.query_params.get('type')
        if qs_type:
            queryset=queryset.filter(requesttype__typecode=qs_type)
        is_pending = self.request.query_params.get('is_pending')
        if is_pending:
            queryset=queryset.filter(payment_status='not',status__in=['pending','approved'])
        payment_status = self.request.query_params.get('payout')
        if payment_status:
            queryset=queryset.filter(payment_status=payment_status)
        qs_status = self.request.query_params.get('status')
        if qs_status:
            queryset=queryset.filter(status=qs_status)
        last_update = self.request.query_params.get('last_update')
        if last_update:
            queryset=queryset.filter(updated_at__gt=last_update)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  
    
class AdvanceRequestExportViewSet(viewsets.ModelViewSet):
    queryset = AdvanceRequest.objects.all()
    serializer_class = AdvanceRequestExportSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get','post']
    pagination_class = StandardResultsSetPagination
    lookup_field = 'request_code'
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        staff=CompanyStaff.objects.get(company__key=key,user__user=user)
        return AdvanceRequest.objects.filter(company=staff.company)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        created_at = request.query_params.get('created_at')
        created_at_from = request.query_params.get('created_at_from')
        created_at_to = request.query_params.get('created_at_to')
        if created_at_from:
            try:
                date_from = make_aware(datetime.combine(parse_date(created_at_from), datetime.min.time()))
                queryset = queryset.filter(created_at__gte=date_from)
            except:
                pass
        if created_at_to:
            try:
                date_to = make_aware(datetime.combine(parse_date(created_at_to), datetime.max.time()))
                queryset = queryset.filter(created_at__lte=date_to)
            except:
                pass
        if created_at:
            try:
                date = make_aware(datetime.combine(parse_date(created_at), datetime.min.time()))
                next_day = make_aware(datetime.combine(parse_date(created_at), datetime.max.time()))
                queryset = queryset.filter(created_at__range=(date, next_day))
            except:
                pass
        staff = self.request.query_params.get('staff')
        if staff:
            queryset=queryset.filter(requester__id=int(staff))
        qs_bankType = self.request.query_params.get('banktype')
        if qs_bankType:
            queryset=queryset.filter(hinhthucThanhtoan=qs_bankType)
        qs_operator = self.request.query_params.get('operator')
        if qs_operator:
            queryset=queryset.filter(operator__id=qs_operator)
        qs_request_code = self.request.query_params.get('request_code')
        if qs_request_code:
            queryset=queryset.filter(request_code__contains=qs_request_code)
        qs_type = self.request.query_params.get('type')
        if qs_type:
            queryset=queryset.filter(requesttype__typecode=qs_type)
        is_pending = self.request.query_params.get('is_pending')
        if is_pending:
            queryset=queryset.filter(payment_status='not',status__in=['pending','approved'])
        payment_status = self.request.query_params.get('payout')
        if payment_status:
            queryset=queryset.filter(payment_status=payment_status)
        qs_status = self.request.query_params.get('status')
        if qs_status:
            queryset=queryset.filter(status=qs_status)
        last_update = self.request.query_params.get('last_update')
        if last_update:
            queryset=queryset.filter(updated_at__gt=last_update)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  
   
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get','post']
    pagination_class = StandardResultsSetPagination
    @action(detail=True, methods=['post'])
    def config(self, request,pk=None):
        company = self.get_object()
        data_config = request.data
        try:
            qs_config=CompanyConfig.objects.get(company=company)
            serializer = CompanyConfigSerializer(qs_config, data=data_config, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'])
    def opCode(self, request,pk=None):
        company = self.get_object()
        operatorCode = request.data.get('operatorCode',None)
        if operatorCode:
            company.operatorCode=operatorCode
            company.save()
            return Response(CompanySerializer(company).data)
        else:
            return Response({"detail": "Vui lòng nhập code mới!"}, status=status.HTTP_403_FORBIDDEN)
    @action(detail=False, methods=['get'])
    def dashboard(self, request,pk=None):
        user = request.user
        key = request.headers.get('ApplicationKey')
        start_date = request.data.get("start_date",now().date())
        end_date = request.data.get("end_date",start_date - timedelta(days=7))
        try:
            staff = CompanyStaff.objects.get(user__user=user, company__key=key)
            company = staff.company
            qs_request = AdvanceRequest.objects.filter(
                company=company,
                created_at__date__range=(end_date, start_date)
            )
            qs_baoung = qs_request.filter(requesttype__typecode="Báo ứng")
            qs_baogiu = qs_request.filter(requesttype__typecode="Báo giữ lương")
            qs_baokhac = qs_request.exclude(
                requesttype__typecode="Báo giữ lương").exclude(
                requesttype__typecode="Báo ứng"
            )
            qs_op = CompanyOperator.objects.filter(company=company).select_related('nhachinh', 'congty_danglam', 'nguoituyen')
            by_nhachinh = defaultdict(int)
            by_customer = defaultdict(lambda: defaultdict(int))
            for op in qs_op:
                nhachinh_name = op.nhachinh.name if op.nhachinh else "other"
                congty_name = op.congty_danglam.name if op.congty_danglam else None
                if op.nhachinh:
                    by_nhachinh[nhachinh_name] += 1
                if congty_name:
                    by_customer[congty_name][nhachinh_name] += 1
            top_nguoi_tuyen = (
                qs_op.values('nguoituyen__id')
                .annotate(total=Count('id'))
                .order_by('-total')[:5]
            )
            today = datetime.now().date()
            return Response({
                "approve": {
                    "total": qs_request.count(),
                    "baoung": AdvanceRequestLTESerializer(qs_baoung, many=True).data,
                    "baogiu": AdvanceRequestLTESerializer(qs_baogiu, many=True).data,
                    "baokhac": AdvanceRequestLTESerializer(qs_baokhac, many=True).data
                },
                "op": {
                    "total": qs_op.count(),
                    "by_nguoituyen": top_nguoi_tuyen,
                    "by_customer": by_customer,
                    "by_nhachinh": by_nhachinh,
                    "homnay": CompanyOperatorDBSerializer(qs_op.filter(ngay_phongvan=today),many=True).data,
                    "dilam": qs_op.filter(congty_danglam__isnull=False).count(),
                    "nhachinh": qs_op.filter(nhachinh__isnull=False).count(),
                },
            }, status=status.HTTP_200_OK)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
     
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        staff=CompanyStaff.objects.get(company__key=key,user__user=user)
        return Company.objects.filter(id=staff.company.id)
    def create(self, request, *args, **kwargs):
        return Response({"detail": "Không được phép tạo mới"}, status=status.HTTP_403_FORBIDDEN)
        # return super().create(request, *args, **kwargs)
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

class MyAdvanceRequestViewSet(viewsets.ModelViewSet):
    queryset = AdvanceRequest.objects.all()
    serializer_class = AdvanceRequestLTESerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        staff=CompanyStaff.objects.get(company__key=key,user__user=user)
        return AdvanceRequest.objects.filter(company=staff.company,requester=staff)
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
    
class AdvanceRequestLTEViewSet(viewsets.ModelViewSet):
    queryset = AdvanceRequest.objects.all()
    serializer_class = AdvanceRequestLTESerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        staff=CompanyStaff.objects.get(company__key=key,user__user=user)
        return AdvanceRequest.objects.filter(company=staff.company)
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        created_at = request.query_params.get('created_at')
        created_at_from = request.query_params.get('created_at_from')
        created_at_to = request.query_params.get('created_at_to')
        approver = request.query_params.get('approver')
        if approver:
            queryset = queryset.filter(approver__id=approver)
        requester = request.query_params.get('requester')
        if requester:
            queryset = queryset.filter(requester__id=requester)
        if created_at_from:
            try:
                date_from = make_aware(datetime.combine(parse_date(created_at_from), datetime.min.time()))
                queryset = queryset.filter(created_at__gte=date_from)
            except:
                pass
        if created_at_to:
            try:
                date_to = make_aware(datetime.combine(parse_date(created_at_to), datetime.max.time()))
                queryset = queryset.filter(created_at__lte=date_to)
            except:
                pass
        if created_at:
            try:
                date = make_aware(datetime.combine(parse_date(created_at), datetime.min.time()))
                next_day = make_aware(datetime.combine(parse_date(created_at), datetime.max.time()))
                queryset = queryset.filter(created_at__range=(date, next_day))
            except:
                pass
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
class AdvanceRequestHistoryViewSet(viewsets.ModelViewSet):
    queryset = AdvanceRequestHistory.objects.all()
    serializer_class = AdvanceRequestHistoryLTESerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        staff=CompanyStaff.objects.get(company__key=key,user__user=user)
        return AdvanceRequestHistory.objects.filter(request__company=staff.company)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        is_payout = request.query_params.get('payout')
        if is_payout:
            queryset = queryset.filter(request__payment_status='done')
        created_at = request.query_params.get('created_at')
        created_at_from = request.query_params.get('created_at_from')
        created_at_to = request.query_params.get('created_at_to')
        if created_at_from:
            try:
                date_from = make_aware(datetime.combine(parse_date(created_at_from), datetime.min.time()))
                queryset = queryset.filter(created_at__gte=date_from)
            except:
                pass
        if created_at_to:
            try:
                date_to = make_aware(datetime.combine(parse_date(created_at_to), datetime.max.time()))
                queryset = queryset.filter(created_at__lte=date_to)
            except:
                pass
        if created_at:
            try:
                date = make_aware(datetime.combine(parse_date(created_at), datetime.min.time()))
                next_day = make_aware(datetime.combine(parse_date(created_at), datetime.max.time()))
                queryset = queryset.filter(created_at__range=(date, next_day))
            except:
                pass
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class CompanyBookViewSet(viewsets.ModelViewSet):
    queryset = CompanyBook.objects.all()
    serializer_class = CompanyBookSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get','post','patch']
    pagination_class = StandardResultsSetPagination
    
    @action(detail=False, methods=['get', 'post'])
    def notebook(self, request):
        user = request.user
        key = request.headers.get('ApplicationKey')
        try:
            staff = CompanyStaff.objects.get(company__key=key, user__user=user)
            qs_book, _ = CompanyBook.objects.get_or_create(title="Note_records", company=staff.company)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'GET':
            return Response(CompanyBookSerializer(qs_book).data)
        elif request.method == 'POST':
            data = request.data.get("data", '')
            old_content = qs_book.content or ''
            if old_content != data:
                diff = list(
                    difflib.unified_diff(
                        old_content.splitlines(),
                        data.splitlines(),
                        fromfile='old',
                        tofile='new',
                        lineterm=''
                    )
                )
                last_history = CompanyBookHistory.objects.filter(book=qs_book).first()
                new_version = 0
                diff_text = ""
                note = "Tạo lần đầu"
                if last_history:
                    diff_text = '\n'.join(diff)
                    added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
                    removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
                    note_parts = []
                    if added: note_parts.append(f"Thêm {added} dòng")
                    if removed: note_parts.append(f"Xoá {removed} dòng")
                    if not note_parts: note_parts.append("Không thay đổi")
                    note = ", ".join(note_parts)
                    last_history = CompanyBookHistory.objects.filter(book=qs_book).first()
                    new_version = (last_history.version + 1)
                CompanyBookHistory.objects.create(
                    book=qs_book,
                    version=new_version,
                    content=data,
                    diff_text=diff_text,
                    edited_by=staff,
                    note=note,
                )
                qs_book.content = data
                qs_book.edited_by = staff
                qs_book.save()
            return Response(CompanyBookSerializer(qs_book).data)
        
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        staff=CompanyStaff.objects.get(company__key=key,user__user=user)
        return CompanyBook.objects.filter(company=staff.company)
    
    def perform_create(self, serializer):
        key = self.request.headers.get('ApplicationKey')
        user = self.request.user
        qs_staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        serializer.save(company=qs_staff.company,edited_by=qs_staff)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        title = request.query_params.get('title')
        if title:
            queryset = queryset.filter(title='title')
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
class CompanyStaffNoteViewSet(viewsets.ModelViewSet):
    queryset = CompanyStaffNote.objects.all()
    serializer_class = CompanyStaffNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        staff=CompanyStaff.objects.get(company__key=key,user__user=user)
        return CompanyStaffNote.objects.filter(user=staff)
    
    def create(self, request, *args, **kwargs):
        key = self.request.headers.get('ApplicationKey')
        user = self.request.user
        staff = CompanyStaff.objects.get(user__user=user, company__key=key)
        if CompanyStaffNote.objects.filter(user=staff).count() >= 3:
            return Response({"detail": "Bạn chỉ được tạo tối đa 3 ghi chú."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=staff)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        title = request.query_params.get('title')
        if title:
            queryset = queryset.filter(title='title')
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)