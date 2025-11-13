from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import os
import uuid
from django.utils import timezone
from django.db.models import Count

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
      
class Baiviet(models.Model):
    user = models.ForeignKey('HRUser', on_delete=models.CASCADE)                 # người đăng bài
    noidung = models.TextField(max_length=600,blank=True,null=True)                 # nội dung bài viết
    lat_location = models.CharField(max_length=20,blank=True,null=True)             # tọa độ
    long_location = models.CharField(max_length=20,blank=True,null=True)            # tọa độ
    location_name = models.TextField(blank=True,null=True)                          # tên địa điểm

    likes = models.ManyToManyField('HRUser',related_name='liked_posts',blank=True)
    shares = models.ManyToManyField('HRUser',related_name='shared_posts',blank=True)
    loadeds = models.ManyToManyField('HRUser',related_name='loaded_posts',blank=True)
    vieweds = models.ManyToManyField('HRUser',related_name='viewd_posts',blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "4.Bài viết"
        verbose_name_plural = "4.Bài viết"
    def __str__(self):
        return f"Bài viết của {self.user.username}"

# Giới hạn mỗi file 200KB và phải là ảnh
MAX_UPLOAD_SIZE = 200 * 1024 # 200 KB
ALLOWED_IMAGE_TYPES = ['image/jpeg','image/jpg','image/png','image/gif','image/webp',]
def validate_image_file(file):
    if file.size > MAX_UPLOAD_SIZE:
        raise ValidationError(f"Kích thước tệp tối đa là {MAX_UPLOAD_SIZE / 1024} KB.")
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(f"Chỉ chấp nhận các loại ảnh JPG, PNG, GIF, hoặc WEBP. Loại tệp hiện tại là {file.content_type}.")
def post_image_upload_path(instance, filename):
    post_id = instance.baiviet.id
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{timestamp}_{uuid.uuid4().hex[:6]}.{ext}"
    return os.path.join('post_images', str(post_id), new_filename)
  
class AnhBaiviet(models.Model):
    baiviet = models.ForeignKey('Baiviet', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=post_image_upload_path,validators=[validate_image_file]) 
    file_name = models.CharField(max_length=225,blank=True,null=True)
    file_type = models.CharField(max_length=80,blank=True,null=True)
    file_size = models.IntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = "6.Ảnh bài viết"
        verbose_name_plural = "6.Ảnh bài viết"
    def __str__(self):
        return f"Ảnh cho Bài viết ID: {self.baiviet.id}"
    def save(self, *args, **kwargs):
        MAX_FILENAME_LENGTH = 180 
        if self.image and self.image.file:
            self.file_size = self.image.file.size 
            original_file_name = os.path.basename(self.image.name)
            if len(original_file_name) > MAX_FILENAME_LENGTH:
                base_name, file_ext = os.path.splitext(original_file_name)
                truncate_length = MAX_FILENAME_LENGTH - len(file_ext)
                if truncate_length < 0:
                     truncate_length = MAX_FILENAME_LENGTH # Cắt toàn bộ nếu tên extension quá dài
                self.file_name = base_name[:truncate_length] + file_ext
            else:
                self.file_name = original_file_name
            try:
                content_type = self.image.file.content_type
                self.file_type = content_type
            except AttributeError:
                self.file_type = os.path.splitext(self.image.name)[1].lstrip('.').lower()
        super().save(*args, **kwargs)
        
class BinhLuan(models.Model):
    baiviet = models.ForeignKey('Baiviet', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('HRUser', on_delete=models.CASCADE) # người comment
    noidung = models.CharField(max_length=180,blank=True,null=True) # nội dung comment
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True,blank=True)
    likes = models.ManyToManyField('HRUser',related_name='liked_comments',blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "5.Bình luận"
        verbose_name_plural = "5.Bình luận"
    def __str__(self):
        return f"Bình luận của {self.user.username}"