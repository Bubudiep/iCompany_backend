from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
      
class ZaloUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)    
    zalo_id = models.CharField(max_length=20, null=True, blank=True)
    zalo_phone = models.CharField(max_length=13, null=True, blank=True)
    username = models.CharField(unique=True,max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Zalo Accounts"
        verbose_name_plural = "Zalo Accounts"
    def save(self, *args, **kwargs):
        if not self.username or not self.password:
            raise ValidationError("Tài khoản và mật khẩu không được để trống.")
        if not self.password.startswith('pbkdf2_sha256$'):  # Kiểm tra xem mật khẩu đã mã hóa chưa
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.username}"

class UserGroup(models.Model):
    key = models.CharField(unique=True,max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    host = models.ForeignKey(ZaloUser, on_delete=models.SET_NULL, null=True, blank=True)
    isGroup = models.BooleanField(default=False)
    member = models.ManyToManyField(ZaloUser, blank=True,
                                  related_name='group_member') # Danh sách thành viên
    approver = models.ManyToManyField(ZaloUser, blank=True,
      related_name='approver_member') # Những người đc phép phê duyệt
    amount_approver = models.ManyToManyField(ZaloUser, blank=True,
      related_name='approver_member') # Những người đc phép phê duyệt khi có tiền
    payment_approver = models.ManyToManyField(ZaloUser, blank=True,
      related_name='approver_member') # Người được bấm nút giải ngân
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Group approver"
        verbose_name_plural = "Group approver"
    def __str__(self):
        return f"{self.name}"
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid4())[:8]  # sinh chuỗi ngắn (tùy chọn độ dài)
        super().save(*args, **kwargs)
        
class ApproveType(models.Model):
    approver = models.ManyToManyField(ZaloUser, blank=True,
      related_name='type_approver_to') # Những người phê duyệt loại này
    
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    
    user = models.ForeignKey(ZaloUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.name}"
      
class ApproveItem(models.Model):
    status_choice=(['pending','Chờ duyệt'],
                   ['approved','Đã duyệt'],
                   ['disbursed','Đã giải ngân'],
                   ['complete','Hoàn thành'],
                   ['cancel','Hủy'],
                   ['reject','Từ chối'])
    author = models.ForeignKey(ZaloUser, on_delete=models.CASCADE, null=True, blank=True)
    types = models.ManyToManyField(ApproveType, blank=True) # Phân loại
    sendto = models.ManyToManyField(
      ZaloUser, blank=True,
      related_name='send_approver_to'
    ) # Gửi đến người duyệt cụ thể
    
    group = models.ForeignKey(UserGroup, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    picture_base64 = models.TextField(null=True, blank=True)
    picture_link = models.CharField(max_length=250, null=True, blank=True)
    
    amount = models.IntegerField(default=0)
    
    status=models.CharField(max_length=100, choices=status_choice, null=True, blank=True)
    rate=models.IntegerField(default=0)
    feedback=models.CharField(max_length=250, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.title}"
class ApproveItemRecord(models.Model):
    status_choice=(['create','Chờ duyệt'],
                   ['approve','Duyệt'],
                   ['disburse','Giải ngân'],
                   ['cancel','Hủy'],
                   ['complete','Hoàn thành'],
                   ['reject','Từ chối'])
    action = models.CharField(max_length=100, choices=status_choice, null=True, blank=True)
    user = models.ForeignKey(ZaloUser, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(max_length=1000,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.id}"