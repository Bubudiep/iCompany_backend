from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Company, ZProfile, ZUsers, 
    RequestNoteCategory, RequestNote, 
    RequestNoteHistory, RequestNoteComment
)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'appid', 'created_at')
    search_fields = ('code', 'name')

@admin.register(ZProfile)
class ZProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'department', 'jobtitle')
    search_fields = ('name', 'phone', 'email', 'cardid')
    list_filter = ('department',)

@admin.register(ZUsers)
class ZUsersAdmin(admin.ModelAdmin):
    list_display = ('zaloid', 'get_name', 'company', 'isvalidated', 'isadmin', 'created_at')
    list_filter = ('isvalidated', 'isadmin', 'company')
    search_fields = ('zaloid', 'zalonumber', 'profile__name')
    raw_id_fields = ('oauth', 'profile', 'company') # Giúp chọn nhanh khi data lớn

    def get_name(self, obj):
        return obj.profile.name if obj.profile else "No Profile"
    get_name.short_description = 'User Name'

@admin.register(RequestNoteCategory)
class RequestNoteCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    list_filter = ('company',)

# Hiển thị lịch sử thay đổi ngay bên trong trang chi tiết của Note
class RequestNoteHistoryInline(admin.TabularInline):
    model = RequestNoteHistory
    extra = 0
    readonly_fields = ('status', 'changed_by', 'changed_at')
    can_delete = False

# Hiển thị comment ngay bên trong trang chi tiết của Note
class RequestNoteCommentInline(admin.StackedInline):
    model = RequestNoteComment
    extra = 1

@admin.register(RequestNote)
class RequestNoteAdmin(admin.ModelAdmin):
    list_display = ('get_thumb', 'title', 'company', 'status', 'author', 'deadline', 'is_urgent')
    list_filter = ('status', 'is_urgent', 'is_public', 'company', 'created_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at' # Thanh điều hướng thời gian
    inlines = [RequestNoteHistoryInline, RequestNoteCommentInline]
    filter_horizontal = ('categories', 'liked', 'viewed', 'favorited', 'pinned') # Giao diện chọn ManyToMany dễ dùng
    
    def get_thumb(self, obj):
        if obj.picture:
            return format_html('<img src="{}" style="width: 50px; height: auto; border-radius: 4px;" />', obj.picture.url)
        return "No Image"
    get_thumb.short_description = 'Ảnh'

@admin.register(RequestNoteHistory)
class RequestNoteHistoryAdmin(admin.ModelAdmin):
    list_display = ('note', 'status', 'changed_by', 'changed_at')
    list_filter = ('status', 'changed_at')

@admin.register(RequestNoteComment)
class RequestNoteCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'note', 'created_at')
    search_fields = ('content',)