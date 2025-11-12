from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

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