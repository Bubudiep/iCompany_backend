from .a import *

class CompanyAccountsViewSet(viewsets.ModelViewSet):
    queryset =CompanyStaff.objects.all()
    serializer_class =CompanyStaffSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        key = self.request.headers.get('ApplicationKey')
        user = self.request.user
        qs_staff=CompanyStaff.objects.get(user__user=user,company__key=key)
        return CompanyStaff.objects.filter(company__key=qs_staff.company.key)
        
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