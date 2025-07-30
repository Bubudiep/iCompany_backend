from django.contrib import admin
from .models import *

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'oauth_user', 'created_at')
    search_fields = ('username',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'phone', 'public')
    search_fields = ('user__username', 'name', 'phone')
    list_filter = ('public', 'gender')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserPlan)
class UserPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'max_storage_mb', 'max_products', 'max_apps', 'max_categories')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserConfigs)
class UserConfigsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserFile)
class UserFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'file_name', 'file_size', 'uploaded_at')
    readonly_fields = ('file_size', 'file_name')
    search_fields = ('user__username', 'file_name')