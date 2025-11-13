from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.core.exceptions import ValidationError
from django.utils.html import format_html

@admin.register(HRUser)
class HRUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'created_at')
    search_fields = ('username', 'user__username')
    readonly_fields = ('user', 'created_at', 'updated_at')
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'verified', 'phone', 'inventer')
    list_filter = ('level', 'verified')
    search_fields = ('username', 'phone')
    autocomplete_fields = ['inventer']

@admin.register(UserConfigs)
class UserConfigsAdmin(admin.ModelAdmin):
    list_display = ('user_username', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Tên tài khoản'

class AnhBaivietInline(admin.TabularInline):
    model = AnhBaiviet
    extra = 1 # Hiển thị thêm 1 hàng trống để thêm ảnh mới
    fields = ('image', 'get_image_preview', 'file_name', 'file_type', 'file_size')
    readonly_fields = ('get_image_preview', 'file_name', 'file_type', 'file_size')
    def get_image_preview(self, obj):
        """Hiển thị ảnh thu nhỏ trong trang Admin."""
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.image.url)
        return "No Image"
    get_image_preview.short_description = 'Preview'
class BinhLuanInline(admin.TabularInline):
    model = BinhLuan
    fields = ('user', 'noidung', 'parent', 'likes', 'created_at')
    readonly_fields = ('user', 'noidung', 'parent', 'likes', 'created_at') # Không cho phép sửa bình luận trực tiếp ở đây
    extra = 0 # Không hiển thị hàng trống để thêm (vì bình luận nên được tạo qua giao diện người dùng)
@admin.register(Baiviet)
class BaivietAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'noidung_preview', 'location_name', 
        'likes_count', 'shares_count', 'viewed_count', 'updated_at')
    fields = ('user', 'noidung', 'location_name', 'lat_location', 
        'long_location', 'likes', 'shares', 'loadeds', 'vieweds')
    list_filter = ('updated_at', 'created_at', 'location_name')
    search_fields = ('noidung', 'location_name', 'user__username')
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
          total_likes=Count('likes', distinct=True),
          total_shares=Count('shares', distinct=True),
          total_vieweds=Count('vieweds', distinct=True))
    def likes_count(self, obj):
        return obj.total_likes
    likes_count.admin_order_field = 'total_likes'
    likes_count.short_description = 'Likes'
    def shares_count(self, obj):
        return obj.total_shares
    shares_count.admin_order_field = 'total_shares'
    shares_count.short_description = 'Shares'
    def viewed_count(self, obj):
        return obj.total_vieweds
    viewed_count.admin_order_field = 'total_vieweds'
    viewed_count.short_description = 'Views'
    def noidung_preview(self, obj):
        return obj.noidung[:50] + '...' if obj.noidung else ''
    noidung_preview.short_description = 'Nội dung'
    inlines = [AnhBaivietInline, BinhLuanInline]

@admin.register(AnhBaiviet)
class AnhBaivietAdmin(admin.ModelAdmin):
    list_display = ('id', 'baiviet', 'file_name', 'file_type', 'file_size', 'created_at')
    readonly_fields = ('file_name', 'file_type', 'file_size')
    list_filter = ('file_type', 'created_at')
    search_fields = ('baiviet__id', 'file_name')
@admin.register(BinhLuan)
class BinhLuanAdmin(admin.ModelAdmin):
    list_display = ('id', 'baiviet', 'user_username', 'parent', 'like_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('noidung', 'user__username', 'baiviet__id')
    raw_id_fields = ('parent', 'baiviet') # Dùng raw_id_fields cho ForeignKey/Self-referential
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Người Bình Luận'
    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Likes'