from django.contrib import admin
from django.utils.html import format_html
from .models import *

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

@admin.register(ZUserNotification)
class ZUserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title','content', 'is_read', 'created_at')
    list_filter = ('user__profile__name',)

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

@admin.register(MailRequest)
class MailRequestAdmin(admin.ModelAdmin):
    # Hiển thị thông tin chính trong danh sách
    list_display = ('subject', 'get_author', 'company', 'isAnonymous', 'isProcessed', 'created_at')
    
    # Bộ lọc nhanh ở cột bên phải
    list_filter = ('isProcessed', 'isAnonymous', 'company', 'created_at')
    
    # Ô tìm kiếm (Search theo tiêu đề, nội dung và tên người gửi)
    search_fields = ('subject', 'message', 'author__profile__name', 'author__zaloid')
    
    # Sắp xếp mặc định
    ordering = ('-created_at',)
    
    # Phân nhóm các trường trong trang chi tiết
    fieldsets = (
        ('Thông tin chung', {
            'fields': ('company', 'author', 'subject', 'isAnonymous')
        }),
        ('Nội dung Mail', {
            'fields': ('message', 'response', 'isProcessed')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Ẩn đi, bấm vào mới hiện
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    # Hàm hiển thị tên author (xử lý trường hợp Anonymous)
    def get_author(self, obj):
        if obj.isAnonymous:
            return "--- Ẩn danh ---"
        return obj.author.profile.name if obj.author and obj.author.profile else obj.author
    get_author.short_description = 'Người gửi'

    # Action: Đánh dấu đã xử lý hàng loạt
    actions = ['mark_as_processed']
    def mark_as_processed(self, request, queryset):
        queryset.update(isProcessed=True)
    mark_as_processed.short_description = "Đánh dấu là Đã xử lý"


@admin.register(QNARequest)
class QNARequestAdmin(admin.ModelAdmin):
    list_display = ('question', 'get_author', 'isAnswered', 'answer_by', 'created_at')
    list_filter = ('isAnswered', 'isAnonymous', 'company')
    search_fields = ('question', 'answer', 'author__profile__name')
    
    # raw_id_fields giúp chọn User nhanh bằng ID/Kính lúp nếu database lớn
    raw_id_fields = ('author', 'answer_by', 'company')
    
    # Cho phép sửa nhanh trạng thái ngay tại danh sách
    list_editable = ('isAnswered',)

    def get_author(self, obj):
        if obj.isAnonymous:
            return "--- Ẩn danh ---"
        return obj.author.profile.name if obj.author and obj.author.profile else "N/A"
    get_author.short_description = 'Người hỏi'
    def save_model(self, request, obj, form, change):
        if change and obj.answer and not obj.answer_by:
            # Lấy ZUser tương ứng với Admin đang login (nếu có)
            from .models import ZUsers
            zuser_admin = ZUsers.objects.filter(oauth=request.user).first()
            if zuser_admin:
                obj.answer_by = zuser_admin
                obj.isAnswered = True
        super().save_model(request, obj, form, change)