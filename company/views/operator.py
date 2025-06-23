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
                staff=CompanyStaff.objects.get(user__user=user,isActive=True,company__key=key)
                if len(operators)>0:
                    listcreated=[]
                    try:
                        with transaction.atomic():  # nếu có lỗi thì rollback tất cả
                            for op in operators:
                                last_id = CompanyOperator.objects.filter(company=staff.company).count()
                                operatorCode=staff.company.operatorCode
                                if not operatorCode:
                                    operatorCode="NLD"
                                count = f"{(last_id+1):06d}"
                                cardID=f"{operatorCode}-{count}"
                                qs_nguoituyen=None
                                nhacungcap=None
                                qs_nhachinh=None
                                if op.get("vendor"):
                                    nhacungcap=CompanyVendor.objects.get(id=op.get("vendor"))
                                if op.get("staff"):
                                    qs_nguoituyen=CompanyStaff.objects.get(id=op.get("staff"),company__key=key)
                                if op.get("nhachinh"):
                                    qs_nhachinh=CompanyVendor.objects.get(id=op.get("nhachinh"),company__key=key)
                                ops=CompanyOperator.objects.create(
                                    company=staff.company,
                                    ngay_phongvan=phongvan,
                                    ma_nhanvien=cardID,
                                    ho_ten=op.get("fullname"),
                                    avatar=op.get("avatar"),
                                    sdt=op.get("phone"),
                                    so_cccd=op.get("cardid"),
                                    ngaysinh=op.get("birthday"),
                                    gioi_tinh=op.get("sex"),
                                    diachi=op.get("address"),
                                    quequan=op.get("address"),
                                    nganhang=op.get("bank_code"),
                                    so_taikhoan=op.get("bank_number"),
                                    chu_taikhoan=op.get("bank_name"),
                                    cccd_front=op.get("cccd_img"),
                                    ghichu=op.get("note"),
                                    nguoituyen=qs_nguoituyen,
                                    nguoibaocao=staff,
                                    vendor=nhacungcap,
                                    nhachinh=qs_nhachinh,
                                    import_raw=op
                                )
                                
                                OperatorUpdateHistory.objects.create(
                                    changed_by=staff,
                                    operator=ops,
                                    old_data=None,
                                    new_data=CompanyOperatorSerializer(ops).data,
                                    notes="Được thêm vào hệ thống"
                                )
                                if op.get('customer'):
                                    qs_customer=CompanyCustomer.objects.filter(id=op.get('customer'),company=staff.company).first()
                                    if qs_customer:
                                        ops.congty_danglam=qs_customer
                                        OperatorWorkHistory.objects.create(
                                            operator=ops,
                                            customer=qs_customer,
                                            nguoituyen=qs_nguoituyen,
                                            ma_nhanvien=op.get('work_code',ops.ma_nhanvien),
                                            start_date=op.get('work_date',None)
                                        )
                                        ops.save()
                                        OperatorUpdateHistory.objects.create(
                                            changed_by=staff,
                                            operator=ops,
                                            old_data=None,
                                            new_data=CompanyOperatorSerializer(ops).data,
                                            notes=f"Bắt đầu đi làm tại {qs_customer.name}"
                                        )
                                listcreated.append(ops)
                            return Response(CompanyOperatorDetailsSerializer(listcreated,many=True).data,
                                            status=status.HTTP_200_OK)
                    except Exception as e:
                        return Response({"detail": f"Lỗi với người lao động: {op.get('fullname')}, lỗi: {str(e)}"},
                                        status=status.HTTP_400_BAD_REQUEST)
            except CompanyStaff.DoesNotExist as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                lineno = exc_tb.tb_lineno
                file_path = exc_tb.tb_frame.f_code.co_filename
                file_name = os.path.basename(file_path)
                print(f"[{file_name}_{lineno}] {str(e)}")
                return Response({"detail": "Tài khoản không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
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
        if qs_res.isSuperAdmin:
            return CompanyOperator.objects.filter(company=qs_res.company)
        return CompanyOperator.objects.filter(Q(nguoituyen=qs_res) | 
                                              Q(nguoibaocao=qs_res) | 
                                              Q(congty_danglam__id__in=qs_res.managerCustomer.all().values_list("id",flat=True)),
                                              company=qs_res.company
                                            )
    
    @action(detail=False, methods=['post'])
    def editlichsu(self, request, pk=None):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        data = request.data.get('data',[])
        try:
            qs_staff = CompanyStaff.objects.get(user__user=user,company__key=key)
            with transaction.atomic():
                return Response({
                }, status=status.HTTP_200_OK)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            return Response({"detail": f"[{file_name}_{lineno}] {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['post'])
    def add_lichsu(self, request, pk=None):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        data = request.data.get('data',[])
        try:
            qs_staff = CompanyStaff.objects.get(user__user=user,company__key=key)
            with transaction.atomic():
                list_op=[]
                list_fail=[]
                for op in data:
                    try:
                        conflict_date=False
                        so_cccd=op.get("cccd")
                        start_date=op.get("start")
                        congty=op.get("congty")
                        nhachinh=op.get("nhachinh")
                        nguoituyen=op.get("nguoituyen")
                        end_date=op.get("end")
                        manhanvien=op.get("manhanvien")
                        tendilam=op.get("fullname")
                        congviec=op.get("congviec")
                        qs_nhachinh=None
                        if start_date:
                            start_date=datetime.strptime(start_date,"%Y-%m-%d").date()
                        if end_date:
                            end_date=datetime.strptime(end_date,"%Y-%m-%d").date()
                        if nhachinh:
                            qs_nhachinh=CompanyVendor.objects.get(name=congty,company=qs_staff.company)
                        qs_op = CompanyOperator.objects.get(so_cccd=so_cccd,
                                                            company=qs_staff.company,
                                                            nhachinh=qs_nhachinh)
                        hist=OperatorWorkHistory.objects.filter(operator=qs_op).order_by('-id')
                        for his in hist:
                            if start_date>=his.start_date and start_date<=his.end_date:
                                conflict_date=True
                            if end_date>=his.start_date and end_date<=his.end_date:
                                conflict_date=True
                        if conflict_date==True:
                            list_fail.append({
                                "so_cccd":so_cccd,
                                "congty":congty,
                                "error": "Ngày làm việc bị trùng",
                            })
                        else:
                            qs_cty=CompanyCustomer.objects.get(name=congty,company=qs_staff.company)
                            qs_nguoituyen=None
                            if nguoituyen:
                                qs_nguoituyen=CompanyStaff.objects.get(id=nguoituyen,company=qs_staff.company)
                            OperatorUpdateHistory.objects.create(
                                operator=qs_op,
                                changed_by=qs_staff,
                                old_data={},
                                new_data=op,
                                notes=f"Thêm lịch sử đi làm ở công ty {qs_cty.name}"
                            )
                            OperatorWorkHistory.objects.create(nguoituyen=qs_nguoituyen,
                                ma_nhanvien=manhanvien,operator=qs_op,
                                ho_ten=tendilam,end_date=end_date,vitri=congviec,
                                customer=qs_cty,nhachinh=qs_nhachinh,
                                start_date=start_date)
                            list_op.append(qs_op.id)
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        lineno = exc_tb.tb_lineno
                        file_path = exc_tb.tb_frame.f_code.co_filename
                        file_name = os.path.basename(file_path)
                        print(f"[{file_name}_{lineno}] {str(e)}")
                return Response({
                    "success": CompanyOperatorMoreDetailsSerializer(list_op,many=True).data,
                    "fail": list_fail
                }, status=status.HTTP_200_OK)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            return Response({"detail": f"[{file_name}_{lineno}] {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
       
    @action(detail=True, methods=['post'])
    def dilam(self, request, pk=None):
        startDate = request.data.get('ngaybatdau',now())
        employeeCode = request.data.get('manhanvien',None)
        company = request.data.get('congty',None)
        cccd_truoc = request.data.get('cccd_truoc',None)
        cccd_sau = request.data.get('cccd_sau',None)
        so_cccd=request.data.get("cccd")
        key = self.request.headers.get('ApplicationKey')
        if company is None:
            return Response({"detail": f"Chưa chọn công ty làm việc!"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            qs_staff = CompanyStaff.objects.get(user__user=request.user,company__key=key)
            with transaction.atomic():
                operator = self.get_object()
                hist=OperatorWorkHistory.objects.filter(operator=operator).order_by('-id')
                if len(hist)!=0:
                    ctyNow=hist.first()
                    if ctyNow.end_date is None:
                        return Response({"detail": f"Chưa nghỉ làm ở công ty cũ!"}, status=status.HTTP_400_BAD_REQUEST)
                    if datetime.strptime(startDate,"%Y-%m-%dT%H:%M:%S.%f%z").date() < ctyNow.end_date:
                        return Response({"detail": "Ngày đi làm không được nhỏ hơn ngày nghỉ ở công ty cũ!"}, status=status.HTTP_400_BAD_REQUEST)
                    
                qs_cty=CompanyCustomer.objects.get(id=company)
                OperatorUpdateHistory.objects.create(
                    operator=operator,
                    changed_by=qs_staff,
                    old_data={"congty_danglam": None if operator.congty_danglam is None else operator.congty_danglam.name},
                    new_data={"congty_danglam":qs_cty.name},
                    notes=f"Báo đi làm ở công ty {qs_cty.name}"
                )
                operator.congty_danglam = qs_cty
                nguoituyen = request.data.get('nguoituyen',None)
                if nguoituyen is not None:
                    qs_nguoituyen=CompanyStaff.objects.get(id=nguoituyen)
                    nguoituyen=qs_nguoituyen
                else:
                    nguoituyen=operator.nguoituyen
                OperatorWorkHistory.objects.create(ma_nhanvien=employeeCode,operator=operator,
                                                nguoituyen=nguoituyen,
                                                customer=qs_cty,so_cccd=so_cccd,
                                                start_date=datetime.strptime(startDate,"%Y-%m-%dT%H:%M:%S.%f%z").date())
                operator.nguoituyen=nguoituyen
                operator.save()
                return Response(CompanyOperatorMoreDetailsSerializer(operator).data, status=status.HTTP_200_OK)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            return Response({"detail": f"[{file_name}_{lineno}] {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def dilamroi(self, request, pk=None):
        user = request.user
        qs_op = self.get_object()
        key = self.request.headers.get('ApplicationKey')
        if company is None:
            return Response({"detail": f"Chưa chọn công ty làm việc!"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            qs_staff = CompanyStaff.objects.get(user__user=user,company__key=key)
            with transaction.atomic():
                conflict_date=False
                so_cccd=request.data.get("cccd")
                start_date=request.data.get("ngaybatdau")
                congty=request.data.get("congty")
                nhachinh=request.data.get("nhachinh")
                nguoituyen=request.data.get("nguoituyen")
                end_date=request.data.get("ngaynghi")
                manhanvien=request.data.get("manhanvien")
                tendilam=request.data.get("fullname")
                congviec=request.data.get("congviec")
                qs_nhachinh=None
                if start_date:
                    start_date=datetime.strptime(start_date,"%Y-%m-%d").date()
                if end_date:
                    end_date=datetime.strptime(end_date,"%Y-%m-%d").date()
                if nhachinh:
                    qs_nhachinh=CompanyVendor.objects.get(name=nhachinh,company=qs_staff.company)
                hist=OperatorWorkHistory.objects.filter(operator=qs_op).order_by('-id')
                for his in hist:
                    if start_date>=his.start_date and start_date<=his.end_date:
                        conflict_date=True
                    if end_date>=his.start_date and end_date<=his.end_date:
                        conflict_date=True
                if conflict_date==True:
                    return Response({"detail": f"Bị trùng lịch sử làm việc"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    qs_cty=CompanyCustomer.objects.get(name=congty,company=qs_staff.company)
                    qs_nguoituyen=None
                    if nguoituyen:
                        qs_nguoituyen=CompanyStaff.objects.get(id=nguoituyen,company=qs_staff.company)
                    OperatorUpdateHistory.objects.create(
                        operator=qs_op,
                        changed_by=qs_staff,
                        old_data={},
                        new_data={},
                        notes=f"Thêm lịch sử đi làm ở công ty {qs_cty.name}"
                    )
                    OperatorWorkHistory.objects.create(nguoituyen=qs_nguoituyen,
                        ma_nhanvien=manhanvien,operator=qs_op,so_cccd=so_cccd,
                        ho_ten=tendilam,end_date=end_date,vitri=congviec,
                        customer=qs_cty,nhachinh=qs_nhachinh,
                        start_date=start_date)
                return Response(CompanyOperatorMoreDetailsSerializer(qs_op).data, status=status.HTTP_200_OK)
        except CompanyCustomer.DoesNotExist:
            return Response({"detail": f"Không tìm thấy công ty"}, status=status.HTTP_400_BAD_REQUEST)
        except CompanyVendor.DoesNotExist:
            return Response({"detail": f"Không tìm thấy nhà chính"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            return Response({"detail": f"[{file_name}_{lineno}] {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def baogiu(self, request, pk=None):
        try:
            user = self.request.user
            key = self.request.headers.get('ApplicationKey')
            operator = self.get_object()
            qs_com=Company.objects.get(key=key)
            ngayUng = request.data.get('ngay',None)
            soTien = request.data.get('sotien',None)
            lyDo = request.data.get('lydo',None)
            qs_staff=CompanyStaff.objects.get(user__user=user,company=qs_com)
            if not soTien:
                return Response({"error": "Thiếu thông tin số tiền."}, status=status.HTTP_400_BAD_REQUEST)
            qs_baogiu, _ = AdvanceType.objects.get_or_create(
                typecode="Báo giữ lương",
                company=qs_com
            )
            qs_res=CompanyStaff.objects.get(user__user=user,isActive=True,company__key=key)
            create_request=AdvanceRequest.objects.create(company=qs_com,
                                requester=qs_res,
                                requesttype=qs_baogiu,
                                operator=operator,
                                amount=soTien,
                                comment=lyDo,
                                request_date= ngayUng,
                                nguoiThuhuong= 'staff',
                            )
            created_data=AdvanceRequestSerializer(create_request).data
            OperatorUpdateHistory.objects.create(
                operator=operator,
                changed_by=qs_staff,
                notes=f"Báo giữ lương {soTien}  [approve|{create_request.request_code}]"
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
    def baoung(self, request, pk=None):
        try:
            user = self.request.user
            key = self.request.headers.get('ApplicationKey')
            operator = self.get_object()
            qs_com=Company.objects.get(key=key)
            soTien = request.data.get('soTien',None)
            lyDo = request.data.get('lyDo',None)
            qs_staff=CompanyStaff.objects.get(user__user=user,company=qs_com)
            ngayUng = request.data.get('ngayUng',now().date())
            if not soTien:
                return Response({"error": "Thiếu thông tin số tiền."}, status=status.HTTP_400_BAD_REQUEST)
            qs_baoung, _ = AdvanceType.objects.get_or_create(
                typecode="Báo ứng",
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
                notes=f"Báo ứng {soTien} [approve|{create_request.request_code}]"
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
                return Response({"detail": f"Chưa đi làm ở công ty nào!"}, status=status.HTTP_400_BAD_REQUEST)
            ctyNow=hist.first()
            if datetime.strptime(ngaynghi,"%Y-%m-%dT%H:%M:%S.%f%z").date() < ctyNow.start_date:
                return Response({"detail": "Ngày nghỉ phải lớn hơn ngày bắt đầu làm!"}, status=status.HTTP_400_BAD_REQUEST)
            if ctyNow.end_date:
                operator.congty_danglam = None
                operator.save()
                return Response({"detail": f"Đang không đi làm!"}, status=status.HTTP_400_BAD_REQUEST)
            OperatorUpdateHistory.objects.create(
                operator=operator,
                changed_by=qs_staff,
                old_data={"congty_danglam":operator.congty_danglam.name},
                new_data={"congty_danglam":None},
                notes=f"Báo nghỉ việc ở công ty {operator.congty_danglam.name}"
            )
            ctyNow.end_date=datetime.strptime(ngaynghi,"%Y-%m-%dT%H:%M:%S.%f%z").date()
            ctyNow.reason=lyDo
            operator.congty_danglam = None
            ctyNow.save()
            operator.save()
            return Response(CompanyOperatorMoreDetailsSerializer(operator).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
          
    @action(detail=True, methods=['post'])
    def bank(self, request, pk=None):
        user=request.user
        key = self.request.headers.get('ApplicationKey')
        qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
        bankname = request.data.get('bankname')
        banknumber = request.data.get('banknumber')
        fullname = request.data.get('fullname')
        try:
            operator = self.get_object()
            if qs_staff!=operator.nguoituyen and qs_staff!=operator.nguoibaocao:
                return Response({"detail": "Bạn không có quyền!"}, status=status.HTTP_400_BAD_REQUEST)
            operator.nganhang=bankname
            operator.so_taikhoan=banknumber
            operator.chu_taikhoan=fullname
            operator.save()
            return Response(CompanyOperatorMoreDetailsSerializer(operator).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
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
            qs_res = CompanyStaff.objects.get(
                user__user=user,
                isActive=True,
                company__key=key
            )
            if not qs_res:
                return Response(
                    {"detail": "Bạn không có quyền!"}, status=status.HTTP_403_FORBIDDEN
                )
            if instance.nguoituyen==qs_res or instance.nguoibaocao==qs_res or instance.congty_danglam in qs_res.managerCustomer.all():
                with transaction.atomic():
                    changed_fields = {'old':{},'new':{}}
                    row_changed = 0
                    for key in request.data:
                        if str(getattr(instance, key)) != str(request.data.get(key)):
                            row_changed = row_changed+1
                            changed_fields['old'][key] = str(getattr(instance, key))
                            changed_fields['new'][key] = str(request.data.get(key))
                    if row_changed>0:
                        OperatorUpdateHistory.objects.create(
                            operator=instance,
                            changed_by=qs_res,
                            old_data=changed_fields['old'],
                            new_data=changed_fields['new'],
                            notes="Cập nhập thông tin người lao động"
                        )
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
        max_update = self.request.query_params.get('max_update')
        if max_update:
            qs_max=CompanyOperator.objects.filter(id=int(max_update)).first()
            if qs_max:
                queryset=queryset.filter(updated_at__gt=qs_max.updated_at)
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
    
class OperatorWorkHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = OP_HISTSerializer
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get','patch']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_res=CompanyStaff.objects.get(user__user=user,isActive=True,company__key=key)
        qs_op=CompanyOperator.objects.filter(company=qs_res.company).values_list('id',flat=True)
        return OperatorWorkHistory.objects.filter(operator__id__in=qs_op)
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