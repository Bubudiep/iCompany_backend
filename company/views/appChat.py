from .a import *

class CompanyStaffViewSet(viewsets.ModelViewSet):
    queryset =CompanyStaff.objects.all()
    serializer_class =CompanyStaffSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get','post']
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        return CompanyStaff.objects.filter(isBan=False,isActive=True,company__key=key)
      
    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        staff = self.get_object()
        chat_message = request.data.get('message',None)
        reply_to = request.data.get('reply_to',None)
        attachment = request.data.get('attachment',None)
        if chat_message is None:
            return Response({"detail": "Chưa có tin nhắn để gửi."},
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            qs_from=CompanyStaff.objects.get(user__user=user,company__key=key)
            room = AppChatRoom.objects.filter(company__key=key,
                        is_group=False,members=staff).filter(members=qs_from).first()
            if not room:
                room = AppChatRoom.objects.create(company=staff.company, is_group=False)
                room.members.add(staff, qs_from)

            if reply_to:
                try:
                  reply_to=ChatMessage.objects.get(id=reply_to,room=room)
                except:
                    return Response({"detail": "Không tìm thấy tin nhắn cần reply."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            crete_mes=ChatMessage.objects.create(
                room=room,
                sender=qs_from,
                message=chat_message,
                reply_to=reply_to,
                attachment=attachment
            )
            return Response(
                ChatMessageSerializer(crete_mes).data,
                status=status.HTTP_201_CREATED
              )
      
    def perform_create(self, serializer):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        if check_permission(user,'CompanyStaff',"create"):
            ...
        return Response(
            {"detail": "Bạn không có quyền thực hiện thao tác này."},
            status=status.HTTP_403_FORBIDDEN
        )
        
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
      
class AppChatRoomViewSet(viewsets.ModelViewSet):
    queryset =AppChatRoom.objects.all()
    serializer_class =AppChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get','post']
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,OrderingFilter)
    filterset_class = AppChatRoomFilter
    ordering_fields = ['created_at', 'last_have_message_at']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_staff = None
        try:
          qs_staff=CompanyStaff.objects.get(user__user=user,isBan=False,isActive=True,company__key=key)
        except:
          ...
        return AppChatRoom.objects.filter(company__key=key,members=qs_staff)
      
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        qs_staff=CompanyStaff.objects.get(user__user=request.user)
        qs_status,_=AppChatStatus.objects.get_or_create(room=instance,user=qs_staff)
        qs_status.last_read_at=now()
        qs_status.save()
        serializer = AppChatRoomDetailSerializer(instance, context=self.get_serializer_context())
        return Response(serializer.data)
      
    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        room = self.get_object()
        chat_message = request.data.get('message',None)
        reply_to = request.data.get('reply_to',None)
        attachment = request.data.get('attachment',None)
        if chat_message is None:
            return Response({"detail": "Chưa có tin nhắn để gửi."},
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            qs_from=CompanyStaff.objects.get(user__user=user,company__key=key)
            if reply_to:
                try:
                  reply_to=ChatMessage.objects.get(id=reply_to,room=room)
                except:
                    return Response({"detail": "Không tìm thấy tin nhắn cần reply."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            crete_mes=ChatMessage.objects.create(
                room=room,
                sender=qs_from,
                message=chat_message,
                reply_to=reply_to,
                attachment=attachment
            )
            return Response(
                ChatMessageSerializer(crete_mes).data,
                status=status.HTTP_201_CREATED
            )
      
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

    
class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset =ChatMessage.objects.all()
    serializer_class =ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,OrderingFilter)
    ordering_fields = ['created_at', 'last_have_message_at']
    def get_queryset(self):
        user = self.request.user
        key = self.request.headers.get('ApplicationKey')
        qs_staff = None
        try:
          qs_staff=CompanyStaff.objects.get(user__user=user,isBan=False,isActive=True,company__key=key)
        except:
          ...
        return ChatMessage.objects.filter(room__members=qs_staff)
      
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        room = self.request.query_params.get('room_id')
        if not room:
            return Response({"detail":"Vui lòng chọn room!"},status=status.HTTP_400_BAD_REQUEST)
        queryset=ChatMessage.objects.filter(room__id=room)
        last = self.request.query_params.get('last_id')
        if last:
            queryset=ChatMessage.objects.filter(id__lt=last)
        page_size = self.request.query_params.get('page_size')
        if page_size is not None:
            self.pagination_class.page_size = int(page_size)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)