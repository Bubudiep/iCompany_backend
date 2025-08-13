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

@admin.register(AppCategorys)
class AppCategorysAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'descriptions', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(UserApps)
class UserAppsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'category', 'app_id', 'created_at', 'updated_at')
    search_fields = ('name', 'user__username', 'app_id')
    list_filter = ('category', 'created_at')
    ordering = ('-created_at',)

@admin.register(UserStore)
class UserStoreAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'store_id', 'user', 'store_hotline', 'created_at', 'updated_at')
    search_fields = ('store_name', 'store_id', 'user__username', 'store_hotline')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('store_id', 'created_at', 'updated_at')


@admin.register(StoreMember)
class StoreMemberAdmin(admin.ModelAdmin):
    list_display = ('store', 'username', 'oauth_user', 'zalo_id', 'email', 'phone', 'last_login', 'created_at', 'updated_at')
    search_fields = ('username', 'zalo_id', 'email', 'phone', 'store__store_name', 'oauth_user__username')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('oauth_user', 'last_login', 'created_at', 'updated_at')


@admin.register(StoreNewsCtl)
class StoreNewsCtlAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'store', 'created_at', 'updated_at')
    search_fields = ('name', 'code', 'store__store_name')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StoreSlides)
class StoreSlidesAdmin(admin.ModelAdmin):
    list_display = ('title', 'store', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'store__store_name')
    list_filter = ('is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StoreCollabs)
class StoreCollabsAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'address', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'store__store_name', 'address')
    list_filter = ('is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StoreNews)
class StoreNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'store', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'short', 'store__store_name', 'category__name')
    list_filter = ('is_active', 'created_at', 'updated_at', 'category')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StoreProductsCtl)
class StoreProductsCtlAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'store', 'created_at', 'updated_at')
    search_fields = ('name', 'code', 'store__store_name')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StoreProducts)
class StoreProductsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'store', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'short', 'store__store_name', 'category__name')
    list_filter = ('is_active', 'created_at', 'updated_at', 'category')
    readonly_fields = ('created_at', 'updated_at')
