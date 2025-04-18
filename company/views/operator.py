from .a import *

class AddOperatorAPIView(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        key = request.headers.get('ApplicationKey')
        user=request.user
        if request.user.is_authenticated:
            try:
                operators=request.data.get("operators")
                phongvan=request.data.get("date")
                staff=CompanyStaff.objects.get(user__user=user,company__key=key)
                if len(operators)>0:
                    listcreated=[]
                    for op in operators:
                        qs_nguoituyen=None
                        if op.get("staff"):
                            qs_nguoituyen=CompanyStaff.objects.get(id=op.get("staff"),company__key=key)
                            
                        last_id = CompanyOperator.objects.filter(company=staff.company).count()
                        operatorCode=staff.company.operatorCode
                        if not operatorCode:
                            operatorCode="NLD"
                        count = f"{last_id:06d}"
                        cardID=f"{operatorCode}-{count}"
                        nhacungcap=None
                        if op.get("type")=="Người của vendor":
                            nhacungcap=CompanyVendor.objects.get(id=nhacungcap)
                        op=CompanyOperator.objects.create(
                            ho_ten=op.get("fullname"),
                            ngay_phongvan=phongvan,
                            avatar=op.get("avatar"),
                            company=staff.company,
                            ma_nhanvien=cardID,
                            sdt=op.get("phone"),
                            so_cccd=op.get("cardid"),
                            ngaysinh=op.get("old"),
                            gioi_tinh=op.get("sex"),
                            diachi=op.get("address"),
                            quequan=op.get("address"),
                            nganhang=op.get("bank_code"),
                            so_taikhoan=op.get("bank_number"),
                            cccd_front=op.get("cccd_img"),
                            ghichu=op.get("note"),
                            nguoituyen=qs_nguoituyen,
                            nguoibaocao=staff,
                            nhacungcap=nhacungcap
                        )
                        OperatorUpdateHistory.objects.create(
                            operator=op,
                            old_data=None,
                            new_data=CompanyOperatorSerializer(op).data,
                            notes="Khởi tạo tài khoản"
                        )
                        listcreated.append(op)
                    return Response(CompanyOperatorDetailsSerializer(listcreated,many=True).data,
                                    status=status.HTTP_200_OK)
                return Response({"detail": "Lỗi khi thêm người lao động"}, status=status.HTTP_200_OK)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                lineno = exc_tb.tb_lineno
                file_path = exc_tb.tb_frame.f_code.co_filename
                file_name = os.path.basename(file_path)
                print(f"[{file_name}_{lineno}] {str(e)}")
                return Response({"detail": "Lỗi khi thêm người lao động"}, status=status.HTTP_400_BAD_REQUEST)
                    
        else:
            return Response({'detail': f"Please login and try again!"}, status=status.HTTP_403_FORBIDDEN)
        
class CompanyOperatorViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyOperatorSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get','patch','delete','post']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=CompanyStaff.objects.get(user__user=user,isActive=True,company__key=key)
        return CompanyOperator.objects.filter(Q(nguoituyen=qs_res) | Q(nguoibaocao=qs_res),company=qs_res.company)
    
    @action(detail=True, methods=['post'])
    def dilam(self, request, pk=None):
        startDate = request.data.get('startDate',now())
        employeeCode = request.data.get('employeeCode',None)
        company = request.data.get('company',None)
        cccd_truoc = request.data.get('cccd_truoc',None)
        cccd_sau = request.data.get('cccd_sau',None)
        if company is None:
            return Response({"detail": f"Chưa chọn công ty làm việc!"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            operator = self.get_object()
            hist=operator_history.objects.filter(operator=operator).order_by('-id')
            if len(hist)!=0:
                ctyNow=hist.first()
                if datetime.strptime(startDate,"%Y-%m-%d").replace(tzinfo=pytz.timezone("Asia/Ho_Chi_Minh")) < ctyNow.end_date:
                    return Response({"detail": "Ngày đi làm không được nhỏ hơn ngày nghỉ ở công ty cũ!"}, status=status.HTTP_400_BAD_REQUEST)
                if ctyNow.end_date is None:
                    return Response({"detail": f"Nhân viên {operator.ho_ten} đang chưa nghỉ làm ở công ty cũ!"}, status=status.HTTP_400_BAD_REQUEST)
            
            qs_cty=company_customer.objects.get(id=company)
            OperatorUpdateHistory.objects.create(
                operator=operator,
                changed_by=qs_staff,
                old_data={"congty_danglam":None},
                new_data={"congty_danglam":qs_cty.name},
                notes=f"Báo đi làm ở công ty {qs_cty.name}"
            )
            operator.congty_danglam = qs_cty
            operator.save()
            nguoituyen = request.data.get('nguoituyen',None)
            if nguoituyen is not None:
                qs_nguoituyen=company_staff.objects.get(id=nguoituyen)
                nguoituyen=qs_nguoituyen
            else:
                nguoituyen=operator.nguoituyen
            OperatorWorkHistory.objects.create(ma_nhanvien=employeeCode,operator=operator,
                                            nguoituyen=nguoituyen,
                                            customer=qs_cty,start_date=startDate)
            return Response(CompanyOperatorMoreDetailsSerializer(operator).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def baoung(self, request, pk=None):
        try:
            user = self.request.user
            key = self.request.headers.get('ApplicationKey')
            operator = self.get_object()
            qs_com=Company.objects.get(key=key)
            soTien = request.data.get('soTien',None)
            lyDo = request.data.get('lyDo',None)
            qs_staff=CompanyStaff.objects.get(user__user=user,company=qs_com)
            ngayUng = request.data.get('ngayUng',datetime.now().date())
            if not soTien:
                return Response({"error": "Thiếu thông tin số tiền."}, status=status.HTTP_400_BAD_REQUEST)
            qs_baoung, _ = AdvanceType.objects.get_or_create(
                typecode="Báo ứng",
                need_operator=True,
                company=qs_com
            )
            qs_res=CompanyStaff.objects.get(user__user=user,isActive=True,company__key=key)
            create_request=AdvanceRequest.objects.create(company=qs_com,
                                requester=qs_res,
                                requesttype=qs_baoung,
                                operator=operator,
                                amount=soTien,
                                comment=lyDo,
                                request_date= ngayUng,
                                hinhthucThanhtoan= request.data.get('hinhthucThanhtoan',None),
                                nguoiThuhuong= request.data.get('nguoiThuhuong',None),
                                khacCtk= request.data.get('khacCtk',None),
                                khacNganhang= request.data.get('khacNganhang',None),
                                khacStk= request.data.get('khacStk',None),
                            )
            created_data=AdvanceRequestSerializer(create_request).data
            OperatorUpdateHistory.objects.create(
                operator=operator,
                changed_by=qs_staff,
                notes=f"Báo ứng {soTien}"
            )
            AdvanceRequestHistory.objects.create(request=create_request,
                                                user=qs_res,action="create",
                                                old_data=None,
                                                new_data=f"{created_data}",
                                                comment="Khởi tạo")
            return Response(CompanyOperatorMoreDetailsSerializer(operator).data, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response({"detail": "Không tìm thấy công ty tương ứng."}, status=status.HTTP_404_NOT_FOUND)
        except CompanyStaff.DoesNotExist:
            return Response({"detail": "Người dùng không thuộc công ty hoặc chưa kích hoạt."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            return Response({"detail": f"[{file_name}_{lineno}] {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def nghiviec(self, request, pk=None):
        user=request.user
        key = self.request.headers.get('ApplicationKey')
        qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
        ngaynghi = request.data.get('ngayNghi',now())
        lyDo = request.data.get('lyDo',None)
        try:
            # xóa cty đang làm, cập nhập lịch sử làm việc tại công ty đang làm
            operator = self.get_object()
            hist=OperatorWorkHistory.objects.filter(operator=operator).order_by('-id')
            if len(hist)==0:
                return Response({"detail": f"Nhân viên {operator.ho_ten} chưa đi làm ở công ty nào!"}, status=status.HTTP_400_BAD_REQUEST)
            ctyNow=hist.first()
            if datetime.strptime(ngaynghi,"%Y-%m-%d").replace(tzinfo=pytz.timezone("Asia/Ho_Chi_Minh")) < ctyNow.start_date:
                return Response({"detail": "Ngày nghỉ phải lớn hơn ngày bắt đầu làm!"}, status=status.HTTP_400_BAD_REQUEST)
            if ctyNow.end_date:
                operator.congty_danglam = None
                return Response({"detail": f"Nhân viên {operator.ho_ten} đang không đi làm!"}, status=status.HTTP_400_BAD_REQUEST)
            OperatorUpdateHistory.objects.create(
                operator=operator,
                changed_by=qs_staff,
                old_data={"congty_danglam":congty_danglam.name},
                new_data={"congty_danglam":None},
                notes=f"Báo nghỉ việc ở công ty {operator.congty_danglam.name}"
            )
            ctyNow.end_date=ngaynghi
            ctyNow.reason=lyDo
            operator.congty_danglam = None
            ctyNow.save()
            operator.save()
            return Response(CompanyOperatorMoreDetailsSerializer(operator).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def perform_create(self, serializer):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res = CompanyStaff.objects.get(
            user__user=user,
            isActive=True,
            company__key=key
        )
        serializer.save(
            company=qs_res.company,
            nguoibaocao=qs_res
        )
        
    def partial_update(self, request, *args, **kwargs):
        try:
            user = self.request.user
            key = self.request.headers.get('ApplicationKey')
            instance = self.get_object()
            qs_res = company_staff.objects.get(
                user__user=user,
                isActive=True,
                company__key=key
            )
            if not qs_res:
                return Response(
                    {"detail": "Bạn không có quyền!"}, status=status.HTTP_403_FORBIDDEN
                )
            if instance.nguoituyen==qs_res or instance.nguoibaocao==qs_res:
                with transaction.atomic():
                    updated_instance=super().partial_update(request, *args, **kwargs)
                    instance.refresh_from_db()
                    return Response(CompanyOperatorMoreDetailsSerializer(instance).data, 
                                status=status.HTTP_200_OK)
            return Response(
                {"detail": "Bạn không có quyền!"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except ObjectDoesNotExist:
            return Response(
                {"detail": "Không tìm thấy dữ liệu!"}, status=status.HTTP_404_NOT_FOUND
            )
        except IntegrityError as e:
            return Response(
                {"detail": "Lỗi cập nhập!"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CompanyOperatorMoreDetailsSerializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        try:
            user = self.request.user
            key = self.request.headers.get('ApplicationKey')
            qs_res = CompanyStaff.objects.get(
                user__user=user,
                isActive=True,
                company__key=key
            )
            if qs_res:
                with transaction.atomic():
                    request.data["nguoibaocao"]=qs_res.id
                    if request.data.get("ma_nhanvien") is None:
                        request.data["ma_nhanvien"]=f"RANDOM_{uuid.uuid4().hex.upper()[:12]}"
                    serializer = self.get_serializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    user_create = serializer.save(company=qs_res.company)
                    return Response(CompanyOperatorMoreDetailsSerializer(user_create).data, status=201)
            else:
                return Response(
                    {"detail": "Bạn không có quyền!"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                name=request.data.get("ma_nhanvien")
                return Response(
                    {"detail": f"Mã nhân viên {name} đã tồn tại!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"detail": "Lỗi khởi tạo!"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class CompanyOperatorDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyOperatorDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=CompanyStaff.objects.get(user__user=user,isActive=True,company__key=key)
        return CompanyOperator.objects.filter(company=qs_res.company)
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class CompanyOperatorMoreDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyOperatorMoreDetailsSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=CompanyStaff.objects.get(user__user=user,isActive=True,company__key=key)
        return CompanyOperator.objects.filter(company=qs_res.company)
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)  # Áp dụng bộ lọc cho queryset
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    