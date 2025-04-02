from django.contrib import admin
from .models import *
from django.utils.html import format_html

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_username',
        'get_email',
        'full_name',
        'phone',
        'gender',
        'date_of_birth',
        'created_at',
    )
    search_fields = ('user__username', 'user__email', 'full_name', 'phone')
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    def avatar_preview(self, obj):
        if obj.avatar_base64:
            return format_html(
                f'<img src="data:image/png;base64,{obj.avatar_base64}" width="50" height="50" style="object-fit:cover;border-radius:5px;" />'
            )
        return "No Avatar"
    avatar_preview.short_description = 'Avatar'
    
@admin.register(CompanyType)
class CompanyTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'user', 'created_at')
    search_fields = ('name', 'code', 'user__username')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'companyType', 'user', 'isActive', 'isValidate', 'isOA')
    search_fields = ('name', 'companyCode', 'user__username')
    list_filter = ('isActive', 'isValidate', 'isOA', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'key')


@admin.register(CompanyDepartment)
class CompanyDepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'parent', 'isActive')
    search_fields = ('name', 'company__name')
    list_filter = ('isActive',)


@admin.register(CompanyPossition)
class CompanyPositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'department', 'parent', 'isActive')
    search_fields = ('name', 'company__name')
    list_filter = ('isActive',)


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'company', 'user', 'created_at')
    search_fields = ('username', 'company__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CompanyStaff)
class CompanyStaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'cardID', 'company', 'user', 'department', 'possition', 'isActive', 'isAdmin', 'isSuperAdmin', 'isBan')
    search_fields = ('cardID', 'user__username', 'company__name')
    list_filter = ('isActive', 'isAdmin', 'isSuperAdmin', 'isBan')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CompanyStaffHistoryFunction)
class StaffHistoryFunctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CompanyStaffHistoryAction)
class StaffHistoryActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CompanyStaffHistory)
class CompanyStaffHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'staff', 'function', 'action', 'title', 'ip_action', 'isReaded', 'created_at')
    search_fields = ('staff__name', 'title', 'message')
    list_filter = ('isReaded', 'isSended', 'isReceived', 'isHidden')
    readonly_fields = ('created_at', 'updated_at')

## miniapp
# === INLINE CONFIG ===
class MiniAppFunctionInline(admin.TabularInline):
    model = MiniAppFunction
    extra = 0
    readonly_fields = ('code','name','is_active', 'public')
    fields = ('code', 'name', 'public', 'description', 'is_active')

class MiniAppPricingInline(admin.TabularInline):
    model = MiniAppPricing
    extra = 0
    fields = ('mini_app', 'price', 'currency', 'duration_in_days', 'is_active')

# === MAIN MODEL ADMIN ===
@admin.register(MiniApp)
class MiniAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'appID', 'isActive', 'public', 'created_at', 'updated_at')
    list_filter = ('isActive', 'public')
    search_fields = ('name', 'appID', 'description')
    inlines = [MiniAppFunctionInline, MiniAppPricingInline]

@admin.register(MiniAppFunction)
class MiniAppFunctionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'public', 'mini_app', 'is_active', 'created_at')
    list_filter = ('is_active', 'mini_app')
    search_fields = ('name', 'code', 'mini_app__name')

@admin.register(MiniAppPricing)
class MiniAppPricingAdmin(admin.ModelAdmin):
    list_display = ('mini_app', 'price', 'currency', 'duration_in_days', 'is_active', 'created_at')
    list_filter = ('currency', 'is_active', 'mini_app')
    search_fields = ('mini_app__name', )

@admin.register(MiniAppSchedule)
class MiniAppScheduleAdmin(admin.ModelAdmin):
    list_display = ('mini_app', 'company', 'start_date', 'end_date', 'is_confirmed', 'created_at')
    list_filter = ('is_confirmed', 'mini_app', 'company')
    search_fields = ('mini_app__name', 'company__name')

@admin.register(MiniAppRegistration)
class MiniAppRegistrationAdmin(admin.ModelAdmin):
    list_display = ('mini_app', 'company', 'registered_at', 'approved')
    list_filter = ('approved', 'mini_app', 'company')
    search_fields = ('mini_app__name', 'company__name')





class ChatAdminGroup(admin.ModelAdmin):
    """Nhóm các model liên quan đến Chat"""
    class Meta:
        verbose_name = "APP Chat"
        verbose_name_plural = "APP Chat"

@admin.register(AppChatRoom)
class AppChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'is_group', 'created_at')
    search_fields = ('name', 'company__name')
    filter_horizontal = ('members',)
    list_filter = ('is_group',)

@admin.register(ChatRoomMembership)
class ChatRoomMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'role', 'joined_at')

@admin.register(ChatDate)
class ChatDateAdmin(admin.ModelAdmin):
    list_display = ('room', 'date', 'total_messages')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'created_at')
    search_fields = ('message', 'sender__name')
    list_filter = ('created_at',)

@admin.register(AppChatStatus)
class AppChatStatusAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'last_read_at')