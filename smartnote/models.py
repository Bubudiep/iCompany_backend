from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class NoteUser(models.Model):
    oauth_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # bạn có thể hash hoặc không tùy nhu cầu
    def __str__(self):
        return self.username
    
class UserProfile(models.Model):
    user = models.OneToOneField(NoteUser, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.full_name or self.user.username
class UserConfigs(models.Model):
    user = models.OneToOneField(NoteUser, on_delete=models.CASCADE, related_name='configs')
    dark_mode = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default="vi")
    notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Cấu hình của {self.user.username}"
    
class UserNotes(models.Model):
    user = models.ForeignKey(NoteUser, on_delete=models.CASCADE, related_name="owned_notes")
    title = models.CharField(max_length=255)
    content = models.TextField()
    pinned = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(
        NoteUser,
        related_name="shared_notes",
        blank=True,
        through='SharedNote'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
    
class SharedNote(models.Model):
    note = models.ForeignKey(UserNotes, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(NoteUser, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)
    class Meta:
        unique_together = ('note', 'shared_with')
    def __str__(self):
        return f"{self.note.title} → {self.shared_with.username}"