from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.utils.timezone import make_aware, datetime
from django.utils.dateparse import parse_date

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
    
class NoteCustomer(models.Model):
    user = models.ForeignKey(NoteUser, on_delete=models.CASCADE,null=True, blank=True)
    hoten = models.CharField(max_length=100,null=True, blank=True)
    sodienthoai = models.CharField(max_length=12,null=True, blank=True)
    description = models.CharField(max_length=200,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"
    
class NoteType(models.Model):
    user = models.ForeignKey(NoteUser, on_delete=models.CASCADE,null=True, blank=True)
    type = models.CharField(max_length=200,null=True, blank=True)
    description = models.CharField(max_length=200,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.id}"
    
class UserNotes(models.Model):
    user = models.ForeignKey(NoteUser, on_delete=models.CASCADE, related_name="owned_notes")
    tenghichu = models.CharField(max_length=255)
    loai = models.ForeignKey(NoteType,on_delete=models.SET_NULL,null=True, blank=True)
    thoigian = models.DateTimeField(null=True, blank=True)
    khachhang = models.ForeignKey(NoteCustomer,on_delete=models.SET_NULL,null=True, blank=True)
    phanloai = models.CharField(default="in",max_length=12,
                                null=True,
                                choices=[['in','in'],['out','out']])
    sotien = models.IntegerField(default=0)
    noidung = models.TextField()
    ghim = models.BooleanField(default=False)
    chiasecho = models.ManyToManyField(
        NoteUser,
        related_name="shared_notes",
        blank=True,
        through='SharedNote'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.tenghichu
    
class SharedNote(models.Model):
    note = models.ForeignKey(UserNotes, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(NoteUser, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)
    class Meta:
        unique_together = ('note', 'shared_with')
    def __str__(self):
        return f"{self.note.title} → {self.shared_with.username}"