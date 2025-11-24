from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import os
import uuid
from django.utils import timezone
from django.db.models import Count
import random
import string

# Giới hạn mỗi file 200KB và phải là ảnh
MAX_UPLOAD_SIZE = 200 * 1024 # 200 KB
ALLOWED_IMAGE_TYPES = ['image/jpeg','image/jpg','image/png','image/gif','image/webp',]
def validate_image_file(file):
    if file.size > MAX_UPLOAD_SIZE:
        raise ValidationError(f"Kích thước tệp tối đa là {MAX_UPLOAD_SIZE / 1024} KB.")
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(f"Chỉ chấp nhận các loại ảnh JPG, PNG, GIF, hoặc WEBP. Loại tệp hiện tại là {file.content_type}.")
def post_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{timestamp}_{uuid.uuid4().hex[:6]}.{ext}"
    return os.path.join('post_images',timestamp,new_filename)
def post_userimage_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{timestamp}_{instance.user.id}_{uuid.uuid4().hex[:6]}.{ext}"
    return os.path.join('post_td_images',timestamp,new_filename)
def post_tdimage_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{timestamp}_{uuid.uuid4().hex[:6]}.{ext}"
    return os.path.join('post_td_images',timestamp,new_filename)
def post_cpimage_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{timestamp}_{uuid.uuid4().hex[:6]}.{ext}"
    return os.path.join('post_cp_images',timestamp, new_filename)
  
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
      
class KhuCongNghiep(models.Model):
    name=models.CharField(max_length=30,unique=True,blank=True,null=True)
    fullname=models.CharField(max_length=100,unique=True,blank=True,null=True)
    image = models.ImageField(upload_to=post_cpimage_upload_path,
                              validators=[validate_image_file],blank=True,null=True) 
    mota=models.CharField(max_length=100,blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "0. Khu công nghiệp"
        verbose_name_plural = "0. Khu công nghiệp"
    def __str__(self):
        return f"{self.name}"
    
class CompanyImages(models.Model):
    image = models.ImageField(upload_to=post_image_upload_path,validators=[validate_image_file]) 
    file_name = models.CharField(max_length=225,blank=True,null=True)
    file_type = models.CharField(max_length=80,blank=True,null=True)
    file_size = models.IntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = "6.0. Ảnh công ty"
        verbose_name_plural = "6.0. Ảnh công ty"
    def __str__(self):
        return f"Ảnh cho công ty {self.file_name}"
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
        
class CompanyLists(models.Model):
    logo = models.ImageField(upload_to='comp_logos/',blank=True,null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # người tạo
    
    name = models.CharField(max_length=100, null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    mota = models.TextField(max_length=1000, null=True, blank=True)
    
    min_tuoi = models.IntegerField(default=10)
    max_tuoi = models.IntegerField(default=50)
    
    address = models.CharField(max_length=255, null=True, blank=True)
    hotline = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    
    is_banned = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    soft_delete = models.BooleanField(default=False)
    address_details = models.JSONField(max_length=255, null=True, blank=True)
    khucongnhiep = models.ForeignKey(KhuCongNghiep, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "6.Danh sách công ty"
        verbose_name_plural = "6.Danh sách công ty"
    def __str__(self):
        return self.name
    
class CompanyPartner(models.Model):
    companies = models.ForeignKey(CompanyLists, on_delete=models.SET_NULL, null=True, blank=True) # người tạo
    admin = models.ManyToManyField('HRUser', blank=True,related_name='companies_admin')
    staff = models.ManyToManyField('HRUser', blank=True,related_name='companies_staff')
    writer = models.ManyToManyField('HRUser', blank=True,related_name='companies_writer')
    partner = models.ManyToManyField('HRUser', blank=True,related_name='companies_partner')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "7.Nhân sự công ty"
        verbose_name_plural = "7.Nhân sự công ty"
    def __str__(self):
        return self.companies.name
    
class BaivietTuyendungTags(models.Model):
    name=models.CharField(max_length=30,unique=True,blank=True,null=True)
    content=models.CharField(max_length=100,blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "8.1 Tin tuyển dụng Tag"
        verbose_name_plural = "8.1 Tin tuyển dụng Tag"
    def __str__(self):
        return f"{self.name}"
        
class BaivietTuyenDungImages(models.Model):
    image = models.ImageField(upload_to=post_tdimage_upload_path,validators=[validate_image_file]) 
    file_name = models.CharField(max_length=225,blank=True,null=True)
    file_type = models.CharField(max_length=80,blank=True,null=True)
    file_size = models.IntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = "8.1. Ảnh bải viết tuyển dụng"
        verbose_name_plural = "8.1. Ảnh bải viết tuyển dụng"
    def __str__(self):
        return f"{self.file_name}"
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
        
class BaivietTuyendung(models.Model):
    code = models.CharField(max_length=32,blank=True,null=True)
    images = models.ManyToManyField(BaivietTuyenDungImages,blank=True)
    tags = models.ManyToManyField(BaivietTuyendungTags,blank=True)
    companies = models.ForeignKey(CompanyLists, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey('HRUser', on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    urgent = models.BooleanField(default=False)
    
    luongtuan = models.BooleanField(default=False)
    phongsach = models.BooleanField(default=False)
    cuatu = models.BooleanField(default=False)
    thuong = models.BooleanField(default=False)
    thuong_sotien = models.IntegerField(default=0)
    thuong_dieukien = models.TextField(max_length=300,blank=True,null=True)
    
    title = models.CharField(max_length=100,blank=True,null=True)
    loaihinh = models.CharField(max_length=20,default='all',choices=[
        ('tv','Thời vụ'),
        ('ct','Chính thức'),
        ('all','Thời vụ và chính thức')
    ],blank=True,null=True)
    calamviec = models.CharField(max_length=20,default='2ca',choices=[
        ('hc','Hành chính'),
        ('2ca','Ca ngày, đêm'),
        ('3ca','3 ca'),
        ('lh','Linh hoạt')
    ],blank=True,null=True)
    
    mucluong = models.CharField(max_length=80,blank=True,null=True)
    luongcoban = models.IntegerField(default=0,blank=True,null=True)
    phucap = models.IntegerField(default=0,blank=True,null=True)
    chuyencan = models.IntegerField(default=0,blank=True,null=True)
    
    yeucau = models.TextField(max_length=600,blank=True,null=True)
    quyenloi = models.TextField(max_length=600,blank=True,null=True)
    noidungbosung = models.TextField(max_length=600,blank=True,null=True)
    
    max_old = models.IntegerField(default=55)
    min_old = models.IntegerField(default=18)
    
    soluong = models.IntegerField(default=100)
    ngayketthuc = models.DateField(null=True,blank=True)
    soft_delete = models.BooleanField(default=False)

    likes = models.ManyToManyField('HRUser',related_name='tuyendung_liked_posts',blank=True)
    shares = models.ManyToManyField('HRUser',related_name='tuyendung_shared_posts',blank=True)
    loadeds = models.ManyToManyField('HRUser',related_name='tuyendung_loaded_posts',blank=True)
    vieweds = models.ManyToManyField('HRUser',related_name='tuyendung_viewd_posts',blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.pk and not self.code:
            now = timezone.now()
            date_prefix = now.strftime("TD-%y%m-")
            last_record = BaivietTuyendung.objects.filter(
                code__startswith=date_prefix,
            ).order_by('-created_at', '-id').first()
            new_sequence = 1
            if last_record and last_record.code:
                try:
                    last_sequence_str = last_record.code.split('-')[-1]
                    last_sequence = int(last_sequence_str)
                    new_sequence = last_sequence + 1
                except ValueError:
                    new_sequence = 1
            sequence_suffix = f"{new_sequence:06d}"
            self.code = date_prefix + sequence_suffix
        super().save(*args, **kwargs)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "8.Tin tuyển dụng"
        verbose_name_plural = "8.Tin tuyển dụng"
    def __str__(self):
        return f"Tin tuyển dụng {self.vitri}_{self.bophan}_{self.companies.name}"
    
class ApplyBaivietTuyendung(models.Model):
    baiviet = models.ForeignKey(BaivietTuyendung, on_delete=models.SET_NULL, null=True, blank=True)
    nguoigioithieu = models.ForeignKey('HRUser', on_delete=models.SET_NULL, 
                                       null=True, blank=True, related_name='nguoi_gioithieu')
    
    nguoiungtuyen = models.ForeignKey('HRUser', on_delete=models.SET_NULL, 
                                      null=True, blank=True, related_name='nguoi_ungtuyen')
    
    sodienthoai = models.TextField(max_length=15,blank=True,null=True)
    hovaten = models.TextField(max_length=50,blank=True,null=True)
    noidungungtuyen = models.TextField(max_length=200,blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "9.Apply vị trí tuyển dụng"
        verbose_name_plural = "9.Apply vị trí tuyển dụng"
    def __str__(self):
        return f"Dự tuyển của {self.baiviet.code}"

class DanhgiaUngvienTags(models.Model):
    name=models.CharField(max_length=30,unique=True,blank=True,null=True)
    content=models.CharField(max_length=100,blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "9.Apply vị trí tuyển dụng"
        verbose_name_plural = "9.Apply vị trí tuyển dụng"
    def __str__(self):
        return f"{self.tagname}"
    
class DanhgiaUngvien(models.Model):
    KETQUA_CHOICES = [
        ('pass', 'Đỗ'),
        ('fail', 'Trượt'),
        ('wait', 'Chờ'),
        ('hold', 'Chưa đánh giá'),
    ]
    baiviet = models.ForeignKey(ApplyBaivietTuyendung, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey('HRUser', on_delete=models.SET_NULL, null=True, blank=True)
    
    ketqua = models.TextField(max_length=50,choices=KETQUA_CHOICES,blank=True,null=True)
    
    ghichu = models.TextField(max_length=200,blank=True,null=True)
    danhgia = models.TextField(max_length=500,blank=True,null=True)
    
    tags = models.ManyToManyField(DanhgiaUngvienTags,blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "10. Đánh giá ứng viên"
        verbose_name_plural = "10. Đánh giá ứng viên"
    def __str__(self):
        return f"Đánh giá {self.baiviet.code}"
    
class UserImage(models.Model):
    user = models.ForeignKey('HRUser', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to=post_userimage_upload_path,validators=[validate_image_file]) 
    album = models.CharField(max_length=80,blank=True,null=True)
    file_name = models.CharField(max_length=225,blank=True,null=True)
    file_type = models.CharField(max_length=80,blank=True,null=True)
    file_size = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = "8.1. Ảnh của người dùng"
        verbose_name_plural = "8.1. Ảnh của người dùng"
    def __str__(self):
        return f"{self.file_name}"
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

def generate_invite_code(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length)) 

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('normal', 'Người tìm việc'),
        ('company', 'Nhà tuyển dụng'),
        ('support', 'Hỗ trợ viên'),
        ('partner', 'Cộng tác viên'),
        ('admin', 'Quản trị viên'),
    ]
    user = models.OneToOneField('HRUser', on_delete=models.CASCADE,related_name='user_fk')
    tag = models.CharField(max_length=20, unique=True, blank=True, null=True)
    avatar = models.ForeignKey(UserImage, on_delete=models.SET_NULL, blank=True, null=True)
    inventer = models.ForeignKey('HRUser', 
        on_delete=models.SET_NULL, 
        null=True, blank=True,related_name='user_inventer'
    )
    invent_code = models.CharField(max_length=30,default="", blank=True, null=True)
    level = models.CharField(max_length=20,default='normal', choices=USER_TYPE_CHOICES)
    verified = models.BooleanField(default=False)
    timviec = models.BooleanField(default=True)
    name_display = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    cccd = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(max_length=300,blank=True, null=True)
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
    def save(self, *args, **kwargs):
        if not self.invent_code or self.invent_code=='':
            safe_chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
            new_code = None
            sub_char="NM"
            if self.level=='admin':
                sub_char="AD"
            if self.level=='company':
                sub_char="HR"
            if self.level=='partner':
                sub_char="PN"
            if self.level=='support':
                sub_char="SP"
            while not new_code:
                suffix = ''.join(random.choice(safe_chars) for _ in range(6))
                temp_code = f"{sub_char}-{suffix}" 
                if not UserProfile.objects.filter(invent_code=temp_code).exists():
                    new_code = temp_code
            self.invent_code = new_code
        super().save(*args, **kwargs)

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
    is_verified = models.BooleanField(default=False)                                # được phê duyệt
    is_hightlight = models.BooleanField(default=False)                              # bị tố cáo

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

class AnhBaiviet(models.Model):
    baiviet = models.ForeignKey('Baiviet', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=post_image_upload_path,validators=[validate_image_file]) 
    file_name = models.CharField(max_length=225,blank=True,null=True)
    file_type = models.CharField(max_length=80,blank=True,null=True)
    file_size = models.IntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = "0. Ảnh bài viết"
        verbose_name_plural = "0. Ảnh bài viết"
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