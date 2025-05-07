from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import User
from datetime import time
from rest_framework import exceptions
import uuid
from django.http import Http404
from decouple import config
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
      
class ZaloUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)    
    zalo_id = models.CharField(max_length=20, null=True, blank=True)
    zalo_phone = models.CharField(max_length=13, null=True, blank=True)
    username = models.CharField(unique=True,max_length=255)
    password = models.CharField(max_length=255)
    isAdmin = models.BooleanField(default=False)
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

class ZaloUserProfile(models.Model):
    user = models.OneToOneField(ZaloUser, on_delete=models.CASCADE)    
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True)
    avatar_base64 = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.full_name}"
    
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
      related_name='amount_approver_member') # Những người đc phép phê duyệt khi có tiền
    payment_approver = models.ManyToManyField(ZaloUser, blank=True,
      related_name='payment_approver_member') # Người được bấm nút giải ngân
    
    last_have_message_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Group approver"
        verbose_name_plural = "Group approver"
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid4())[:18].upper()
        super().save(*args, **kwargs)
        
class UserGroupRecord(models.Model):
    user = models.ForeignKey(ZaloUser, on_delete=models.CASCADE) 
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    success = models.BooleanField(default=False)
    action = models.CharField(max_length=100, null=True, blank=True)
    comment = models.CharField(max_length=100, null=True, blank=True)
    detail = models.CharField(max_length=200, null=True, blank=True)
    target = models.ForeignKey(ZaloUser, on_delete=models.CASCADE, 
                               related_name="UserGroupRecord_target") 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.group.name} - {self.last_check}"
      
class LastCheckGroup(models.Model):
    user = models.ForeignKey(ZaloUser, on_delete=models.CASCADE) 
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    last_check = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-last_check']
    def __str__(self):
        return f"{self.group.name} - {self.last_check}"
  
class ApproveType(models.Model):
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, null=True, blank=True)
    approver = models.ManyToManyField(ZaloUser, blank=True,
      related_name='type_approver_to') # Những người phê duyệt loại này
    amount_approver = models.ManyToManyField(ZaloUser, blank=True,
      related_name='type_amount_approver_member') # Những người đc phép phê duyệt khi có tiền
    payment_approver = models.ManyToManyField(ZaloUser, blank=True,
      related_name='type_payment_approver_member') # Người được bấm nút giải ngân
    
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    
    user = models.ForeignKey(ZaloUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
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
    
    status=models.CharField(max_length=100,default='pending', choices=status_choice, null=True, blank=True)
    rate=models.IntegerField(default=0)
    feedback=models.CharField(max_length=250, null=True, blank=True)
    
    last_have_message_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-last_have_message_at']
    def __str__(self):
        return f"{self.title}"
      
class LastCheckItem(models.Model):
    user = models.ForeignKey(ZaloUser, on_delete=models.CASCADE) 
    item = models.ForeignKey(ApproveItem, on_delete=models.CASCADE)
    last_check = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.item.title} - {self.last_check}"
    class Meta:
        ordering = ['-last_check']
      
class ApproveItemRecord(models.Model):
    status_choice=(['create','Chờ duyệt'],
                   ['approve','Duyệt'],
                   ['disburse','Giải ngân'],
                   ['cancel','Hủy'],
                   ['complete','Hoàn thành'],
                   ['reject','Từ chối'])
    item = models.ForeignKey(ApproveItem, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100, choices=status_choice, null=True, blank=True)
    user = models.ForeignKey(ZaloUser, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(max_length=1000,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.id}"
    class Meta:
        ordering = ['-id']
      
class ApproveItemMessage(models.Model):
    item = models.ForeignKey(ApproveItem, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(ZaloUser, on_delete=models.SET_NULL, null=True, blank=True)
    reply = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(max_length=1000,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.id}"
    class Meta:
        ordering = ['-id']
        
class ApproveItemEmoji(models.Model):
    emoji_choice=(['like','Thích'],
                  ['tym','Thả tim'],
                  ['haha','Haha'],
                  ['sad','Buồn'],
                  ['vl','Vler'],
                  ['wow','Ồ'],
                  ['angry','Dỗi'])
    item = models.ForeignKey(ApproveItem, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(ZaloUser, on_delete=models.SET_NULL, null=True, blank=True)
    emoji = models.CharField(default="like",max_length=20,choices=emoji_choice)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.id}"
    class Meta:
        ordering = ['-id']

@receiver(post_save, sender=ApproveItem)
def handle_ApproveItem_save(sender, instance, created, **kwargs):
    if created:
        instance.group.last_have_message_at = now()
        instance.group.save()
        cr_record=ApproveItemRecord.objects.create(item=instance,
                                         action="create",
                                         user=instance.author)

@receiver(post_save, sender=ApproveItemMessage)
def handle_ApproveItemMessage_save(sender, instance, created, **kwargs):
    if created:
        instance.item.last_have_message_at = now()
        instance.item.save()
        LastCheckItem.objects.update_or_create(item=instance.item,
                                          user=instance.user,
                                          last_check=now())