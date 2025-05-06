from django.contrib import admin
from .models import *
from django.contrib.auth.hashers import make_password

@admin.register(ZaloUser)
class ZaloUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'zalo_id', 'zalo_phone', 'created_at']
    search_fields = ['username', 'zalo_id', 'zalo_phone']
    readonly_fields = ['created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        if not obj.password.startswith('pbkdf2_sha256$'):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'key', 'host', 'isGroup']
    search_fields = ['name', 'key']
    filter_horizontal = ['member', 'approver', 'amount_approver', 'payment_approver']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ApproveType)
class ApproveTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'user']
    search_fields = ['name', 'description']
    filter_horizontal = ['approver']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ApproveItem)
class ApproveItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'amount', 'status', 'created_at']
    search_fields = ['title', 'description']
    list_filter = ['status']
    filter_horizontal = ['types', 'sendto']
    readonly_fields = ['created_at', 'updated_at']
    
@admin.register(ApproveItemRecord)
class ApproveItemRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'action', 'created_at']
    search_fields = ['comment']
    list_filter = ['action']
    readonly_fields = ['created_at']
