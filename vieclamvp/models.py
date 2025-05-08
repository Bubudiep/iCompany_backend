from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import User
from datetime import time
from rest_framework import exceptions
import uuid
from django.http import Http404
from rest_framework import status
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import random
import string
from datetime import datetime, timedelta
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
import time as time_module
from django.db.models.signals import post_save, pre_save, post_migrate
from django.dispatch import receiver
from rest_framework.exceptions import NotFound
from django.db import transaction

# tên column cách nhau bởi _ và không có viết hoa
     
class JobsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(unique=True, max_length=255)  # tên đăng nhập riêng
    password = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Tài khoản"
        verbose_name_plural = "Danh sách tài khoản"

    def save(self, *args, **kwargs):
        if not self.username or not self.password:
            raise ValidationError("Tài khoản và mật khẩu không được để trống.")
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        if not self.user:
            full_username = f"jobs_{self.username}"
            if User.objects.filter(username=full_username).exists():
                raise ValidationError("User đã tồn tại.")
            user = User.objects.create(username=full_username)
            self.user = user
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
      
class JobsUserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('candidate', 'Người tìm việc'),
        ('employer', 'Nhà tuyển dụng'),
    ]

    jobs_user = models.OneToOneField('JobsUser', on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20,default='candidate', choices=USER_TYPE_CHOICES)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Nếu là nhà tuyển dụng thì phải có company_name
        if self.user_type == 'employer' and not self.company_name:
            raise ValidationError("Nhà tuyển dụng phải có tên công ty.")

    def __str__(self):
        return f"{self.jobs_user.username} ({self.get_user_type_display()})"
