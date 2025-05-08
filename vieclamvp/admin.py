from django.contrib import admin
from .models import *

@admin.register(JobsUser)
class JobsUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'user', 'is_admin', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'user')  # không cho chỉnh user sau khi tạo
    fields = ('username', 'password', 'is_admin', 'user', 'created_at', 'updated_at')
    search_fields = ('username', 'user__username')
