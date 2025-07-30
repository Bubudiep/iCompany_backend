from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import User
from datetime import time
from rest_framework import exceptions
import uuid
from django.utils.timezone import make_aware, datetime
from django.utils.dateparse import parse_date
from django.db.models import Q,F
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import random
import string
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.db.models import F
import socketio
from django.core.exceptions import ObjectDoesNotExist
import time as time_module
from collections import defaultdict
from django.db.models import Count
import base64
from PIL import Image
from io import BytesIO
import difflib
from django.core.files.storage import default_storage

class Users(models.Model):
    oauth_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        if not self.oauth_user:
            user = User.objects.create(
                username=f"vietz_user_{self.username}",
                password=self.password,
            )
            self.oauth_user = user
        super().save(*args, **kwargs)
    def __str__(self):
        return self.username
    
class UserProfile(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    public = models.BooleanField(default=True)
    name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Nam'), ('female', 'Nữ')], blank=True)
    avatar = models.URLField(blank=True, null=True)
    avatar_base64 = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Profile of {self.user.username}"
      
class UserPlan(models.Model):
    name = models.CharField(max_length=100, unique=True)  # "Free", "Pro", "Enterprise"...
    max_storage_mb = models.IntegerField(default=300)
    max_apps = models.IntegerField(default=5)
    max_categories = models.IntegerField(default=5)
    max_products = models.IntegerField(default=30)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    
class UserConfigs(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    plan = models.ForeignKey(UserPlan, on_delete=models.SET_NULL, null=True, blank=True)
    config = models.JSONField(default=dict,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Cấu hình của {self.user.username}"
    
class UserFile(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='uploads/viez/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # lưu theo byte
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if self.file: # Tự động lấy kích thước và tên file
            self.file_name = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.user.username} - {self.file_name} ({self.file_size / 1024:.1f} KB)"
    def delete(self, *args, **kwargs):
        if self.file:
            if default_storage.exists(self.file.name):
                default_storage.delete(self.file.name) # Xoá file vật lý khi record bị xoá
        super().delete(*args, **kwargs)