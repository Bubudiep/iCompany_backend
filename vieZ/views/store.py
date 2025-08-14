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