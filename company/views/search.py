from .a import *

class SearchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()  # Lấy từ khóa tìm kiếm
        search_type = request.query_params.get('type', '').strip()
        key = request.headers.get('ApplicationKey')
        user=request.user
        staff=CompanyStaff.objects.get(user__user=user,company__key=key)
        if not query:
            return Response({"detail": "Hãy nhập từ khóa tìm kiếm."}, status=400)
        if search_type == 'employee':
            results = CompanyStaffProfile.objects.filter(
              Q(staff__company=staff.company)&Q(
                Q(staff__cardID__icontains=query) | 
                Q(staff__user__username__icontains=query)| 
                Q(full_name__icontains=query)| 
                Q(nick_name__icontains=query)| 
                Q(phone__icontains=query)
              )
            )
            results=results.annotate(
                username=F('staff__user__username'),
                name=F('staff__cardID')
            ).values('id', 'name', 'username')[:8]
        elif search_type == 'department':
            results = CompanyDepartment.objects.filter(
              company=staff.company,
              name__icontains=query
            ).values('id', 'name')
        elif search_type == 'position':
            results = CompanyPossition.objects.filter(
              company=staff.company,
              name__icontains=query
            ).values('id', 'name')
        elif search_type == 'operator':
            results = CompanyOperator.objects.filter(
              Q(company=staff.company)&
              Q(Q(ho_ten__icontains=query)|
                Q(ma_nhanvien__icontains=query)|
                Q(ten_goc__icontains=query)|
                Q(so_cccd__icontains=query)|
                Q(so_taikhoan__icontains=query)|
                Q(chu_taikhoan__icontains=query)|
                Q(ghichu__icontains=query)|
                Q(ghichu__icontains=query)|
                Q(nguoituyen__name__icontains=query)|
                Q(nguoituyen__CompanyStaffProfile__full_name__icontains=query)|
                Q(nguoibaocao__name__icontains=query)|
                Q(nguoibaocao__CompanyStaffProfile__full_name__icontains=query))
            ).values('id', 'ma_nhanvien','ho_ten')[:8]
        else:
            return Response({"detail": "Không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(results)
  