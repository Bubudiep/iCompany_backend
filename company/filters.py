from .models import *
import django_filters

class AppChatRoomFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')  # Lọc theo tên không phân biệt hoa thường
    is_group = django_filters.BooleanFilter()
    created_at = django_filters.DateFromToRangeFilter()  # Lọc theo khoảng ngày

    class Meta:
        model = AppChatRoom
        fields = ['name', 'is_group', 'created_at']