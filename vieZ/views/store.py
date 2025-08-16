from .a import *

class StoreNewsViewSet(viewsets.ModelViewSet):
    queryset = StoreNews.objects.all()
    serializer_class = StoreNewsSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagesPagination
    http_method_names = ['get']
    def get_queryset(self):
        key = self.request.headers.get('StoreKey')
        return StoreNews.objects.filter(store__store_id=key).order_by('-updated_at')
    def retrieve(self, request, *args, **kwargs):
        return Response(UserAppDetailSerializer(self.get_object()).data)
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
class StoreFeedbacksViewSet(viewsets.ModelViewSet):
    queryset = StoreFeedbacks.objects.all()
    serializer_class = StoreFeedbacksSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagesPagination
    http_method_names = ['get']
    def get_queryset(self):
        key = self.request.headers.get('StoreKey')
        return StoreFeedbacks.objects.filter(store__store_id=key).order_by('-updated_at')
    def retrieve(self, request, *args, **kwargs):
        return Response(UserAppDetailSerializer(self.get_object()).data)
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
class StoreCollabsViewSet(viewsets.ModelViewSet):
    queryset = StoreCollabs.objects.all()
    serializer_class = StoreCollabsSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagesPagination
    http_method_names = ['get']
    def get_queryset(self):
        key = self.request.headers.get('StoreKey')
        return StoreCollabs.objects.filter(store__store_id=key).order_by('-updated_at')
    def retrieve(self, request, *args, **kwargs):
        return Response(UserAppDetailSerializer(self.get_object()).data)
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
class StoreSlidesViewSet(viewsets.ModelViewSet):
    queryset = StoreSlides.objects.all()
    serializer_class = StoreSlidesSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagesPagination
    http_method_names = ['get']
    def get_queryset(self):
        key = self.request.headers.get('StoreKey')
        return StoreSlides.objects.filter(store__store_id=key).order_by('-updated_at')
    def retrieve(self, request, *args, **kwargs):
        return Response(UserAppDetailSerializer(self.get_object()).data)
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
class StoreProductsViewSet(viewsets.ModelViewSet):
    queryset = StoreProducts.objects.all()
    serializer_class = StoreProductsSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagesPagination
    http_method_names = ['get']
    def get_queryset(self):
        key = self.request.headers.get('StoreKey')
        return StoreProducts.objects.filter(store__store_id=key).order_by('-updated_at')
    def retrieve(self, request, *args, **kwargs):
        return Response(UserAppDetailSerializer(self.get_object()).data)
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

class MemberOrder(APIView):
    authentication_classes = [OAuth2Authentication]  # Kiểm tra xác thực OAuth2
    permission_classes = [IsAuthenticated]  # Đảm bảo người dùng phải đăng nhập (token hợp lệ)
    def post(self, request):
        try:
            key = request.headers.get('StoreKey')
            item = request.data.get('item')
            member = StoreMember.objects.get(oauth_user=request.user)
            qs_cart = MemberCart.objects.filter(id__in=item,member=member)
            with transaction.atomic():
                order=Order.objects.create(
                  store=member.store,
                  customer=member,
                  status="pending"
                )
                totalcost=0
                for od in qs_cart:
                    od_item=OrderItem.objects.create(
                      order=order,
                      product=od.product,
                      quantity=od.quantity,
                      price=od.product.price,
                    )
                    totalcost=totalcost+(od.product.price*od.quantity)
                    od.is_ordered=True
                    od.save()
                order.total_amount=totalcost
                order.save()
                OrderHistory.objects.create(
                  order=order,
                  user=member,
                  action="Create",
                  note="Tạo đơn hàng"
                )
                return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            lineno = exc_tb.tb_lineno
            file_path = exc_tb.tb_frame.f_code.co_filename
            file_name = os.path.basename(file_path)
            return Response(
              {
                "message":"Phát sinh lỗi khi đặt đơn hàng!",
                "possition":f"{file_name}_{lineno}",
                "detail":str(e)
              }, 
              status=status.HTTP_400_BAD_REQUEST
            )
             
class MemberCartViewSet(viewsets.ModelViewSet):
    queryset = MemberCart.objects.all()
    serializer_class = MemberCartSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagesPagination
    def perform_create(self, serializer):
        key = self.request.headers.get('StoreKey')
        qs_member=StoreMember.objects.get(
          oauth_user=self.request.user,
          store__store_id=key
        )
        serializer.save(member=qs_member)
    def create(self, request, *args, **kwargs):
        key = self.request.headers.get('StoreKey')
        qs_member=StoreMember.objects.get(
          oauth_user=self.request.user,
          store__store_id=key
        )
        qs_item=MemberCart.objects.filter(product=request.data.get('product')).first()
        if (qs_item):
            qs_item.quantity=qs_item.quantity+request.data.get('quantity')
            qs_item.save()
            serializer = self.get_serializer(qs_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return super().create(request, *args, **kwargs)
      
    def get_queryset(self):
        key = self.request.headers.get('StoreKey')
        qs_member=StoreMember.objects.get(
          oauth_user=self.request.user,
          store__store_id=key
        )
        return MemberCart.objects.filter(
          member=qs_member
        ).order_by('-updated_at')
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
      
class MemberOderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagesPagination
    http_method_names = ['get']
    def get_queryset(self):
        key = self.request.headers.get('StoreKey')
        qs_member=StoreMember.objects.get(
          oauth_user=self.request.user,
          store__store_id=key
        )
        return Order.objects.filter(
          customer=qs_member
        ).order_by('-updated_at')
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