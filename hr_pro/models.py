from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

class HRUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(unique=True, max_length=255)  # tên đăng nhập riêng
    password = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "1.Tài khoản"
        verbose_name_plural = "1.Danh sách tài khoản"
    def save(self, *args, **kwargs):
        if not self.username or not self.password:
            raise ValidationError("Tài khoản và mật khẩu không được để trống.")
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        if not self.user:
            full_username = f"HRPro_{self.username}"
            if User.objects.filter(username=full_username).exists():
                raise ValidationError("User đã tồn tại.")
            user = User.objects.create(username=full_username)
            self.user = user
        super().save(*args, **kwargs)
    def __str__(self):
        return self.username
      
class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('normal', 'Người tìm việc'),
        ('company', 'Nhà tuyển dụng'),
        ('support', 'Hỗ trợ viên'),
        ('partner', 'Cộng tác viên'),
        ('admin', 'Quản trị viên'),
    ]
    user = models.OneToOneField('HRUser', on_delete=models.CASCADE,related_name='user_fk')
    tag = models.CharField(max_length=20,unique=True, blank=True, null=True)
    inventer = models.ForeignKey('HRUser', 
                                 on_delete=models.SET_NULL, 
                                 null=True, blank=True,related_name='user_inventer')
    level = models.CharField(max_length=20,default='normal', choices=USER_TYPE_CHOICES)
    verified = models.BooleanField(default=False)
    timviec = models.BooleanField(default=True)
    name_display = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "2.Thông tin người dùng"
        verbose_name_plural = "2.Thông tin người dùng"
    def clean(self):
        if self.level == 'company' and not self.company:
            raise ValidationError("Nhà tuyển dụng phải có tên công ty.")
    def __str__(self):
        return f"{self.user.username} {self.name}"

class UserConfigs(models.Model):
    user = models.OneToOneField('HRUser', on_delete=models.CASCADE)
    raw_config = models.JSONField(blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "3.Cấu hình người dùng"
        verbose_name_plural = "3.Cấu hình người dùng"
    def __str__(self):
        return f"Cấu hình của {self.user.username}"
    