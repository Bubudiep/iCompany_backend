from django.contrib import admin
from .models import NoteUser, UserProfile, UserConfigs, UserNotes, SharedNote

@admin.register(NoteUser)
class NoteUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'oauth_user']
    search_fields = ['username', 'oauth_user__username']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'birthdate']
    search_fields = ['full_name', 'user__username']

@admin.register(UserConfigs)
class UserConfigsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'dark_mode', 'language', 'notifications_enabled']
    list_filter = ['dark_mode', 'language', 'notifications_enabled']

@admin.register(UserNotes)
class UserNotesAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'pinned', 'created_at', 'updated_at']
    search_fields = ['title', 'user__username']
    list_filter = ['pinned', 'created_at']

@admin.register(SharedNote)
class SharedNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'note', 'shared_with', 'can_edit']
    list_filter = ['can_edit']
    search_fields = ['note__title', 'shared_with__username']
