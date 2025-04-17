from .a import *
from .company import Company, CompanyStaff

class MiniApp(models.Model):
    appID = models.CharField(max_length=200, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    public = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
      
class MiniAppFunction(models.Model):
    mini_app = models.ForeignKey(MiniApp, on_delete=models.CASCADE, related_name='functions')
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200,null=True, blank=True)
    is_active = models.BooleanField(default=True)
    public = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('mini_app', 'code')

    def __str__(self):
        return f"{self.mini_app.name} - {self.name}"
   
class MiniAppPricing(models.Model):
    mini_app = models.ForeignKey(MiniApp, on_delete=models.CASCADE, related_name='pricings')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='VND')  # hoặc USD, EUR tùy
    duration_in_days = models.PositiveIntegerField(default=30)  # thời gian thuê theo gói
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.mini_app.name} - {self.price} {self.currency} / {self.duration_in_days} days"
      
class MiniAppSchedule(models.Model):
    mini_app = models.ForeignKey(MiniApp, on_delete=models.CASCADE, related_name='schedules')
    start_date = models.DateField()
    end_date = models.DateField()
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='miniapp_schedules')
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('mini_app', 'company', 'start_date', 'end_date')

    def __str__(self):
        return f"{self.company.name} thuê {self.mini_app.name} từ {self.start_date} đến {self.end_date}"
      
class MiniAppRegistration(models.Model):
    mini_app = models.ForeignKey(MiniApp, on_delete=models.CASCADE, related_name='registrations')
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='app_registrations')
    registered_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('mini_app', 'company')

    def __str__(self):
        return f"{self.company.name} đăng ký {self.mini_app.name}"

class MiniAppConfigs(models.Model):
    mini_app = models.ForeignKey(MiniApp, on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    members_list = models.ManyToManyField(CompanyStaff)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('mini_app', 'company')

    def __str__(self):
        return f"{self.company.name} đăng ký {self.mini_app.name}"
    
## Chat theo nhóm hoặc cá nhân, trong nhóm sẽ có chat Message
## Kiểm tra xem người dùng đã đọc lần cuối vào lúc nào, query ra số lượng tin nhắn chưa đọc
class AppChatRoom(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    avatar = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)  # Chỉ dùng cho nhóm
    is_group = models.BooleanField(default=False)  # Xác định nhóm hay chat cá nhân
    members = models.ManyToManyField(CompanyStaff,related_name="appchatroom_members")
    admins = models.ManyToManyField(CompanyStaff,related_name="appchatroom_admins")
    host = models.ForeignKey(CompanyStaff,on_delete=models.SET_NULL,null=True,related_name="appchatroom_host")
    members_change_avatar = models.BooleanField(default=True)
    members_change_name = models.BooleanField(default=True)
    members_add_members = models.BooleanField(default=True)
    members_remove_members = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_have_message_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-last_have_message_at']
    def __str__(self):
        return f"{self.name if self.is_group else 'Private Chat'} - {self.company.name}"
    
class ChatRoomMembership(models.Model):
    MEMBER_TYPES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('guest', 'Guest'),
    )
    user = models.ForeignKey(CompanyStaff, on_delete=models.CASCADE, related_name='chat_room_memberships')
    room = models.ForeignKey(AppChatRoom, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=MEMBER_TYPES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.room.name} as {self.get_role_display()}"
    
def chat_attachment_upload_path(instance, filename):
    """Tạo đường dẫn lưu file theo phòng chat."""
    return f"chat_attachments/{instance.room.id}/{filename}"

class ChatDate(models.Model):
    room = models.ForeignKey(AppChatRoom, on_delete=models.CASCADE, related_name="chat_dates")
    date = models.DateField(auto_now_add=True)
    total_messages = models.PositiveIntegerField(default=0) 
    class Meta:
        unique_together = ('room', 'date')
        ordering = ['-date']
    def __str__(self):
        return f"{self.room} - {self.date} ({self.total_messages} messages)"
    
class ChatMessage(models.Model):
    def validate_attachment_file_type(value):
        valid_mime_types = ['image/jpeg', 'image/png', 'application/pdf']
        file_type = value.file.content_type
        if file_type not in valid_mime_types:
            raise ValidationError("Chỉ chấp nhận file ảnh hoặc PDF.")
    isAction = models.BooleanField(default=False)
    ghim_by = models.ForeignKey(CompanyStaff, on_delete=models.SET_NULL, null=True, blank=True, related_name="ghim_messages")
    room = models.ForeignKey(AppChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CompanyStaff, on_delete=models.CASCADE, related_name="sent_messages")
    message = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to=chat_attachment_upload_path, null=True, blank=True, 
                                  validators=[validate_attachment_file_type])
    socket_sended = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    mention_users = models.ManyToManyField(CompanyStaff, related_name='mentioned_in_messages', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-id']
    def clean(self):
        """Giới hạn kích thước file đính kèm không vượt quá 1MB"""
        if self.attachment:
            max_size = 1 * 1024 * 1024  # 1MB
            if self.attachment.size > max_size:
                raise ValidationError("File đính kèm không được vượt quá 1MB.")
            
    def __str__(self):
        return f"{self.message[:20]}" if self.message else "Attachment"
    
class AppChatStatus(models.Model):
    room = models.ForeignKey(AppChatRoom, on_delete=models.CASCADE, related_name="chat_status")
    user = models.ForeignKey(CompanyStaff, on_delete=models.CASCADE, related_name="chat_status")
    last_read_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.room}"
    
class LastCheckAPI(models.Model):
    function_name = models.CharField(max_length=100)
    user = models.ForeignKey(CompanyStaff, on_delete=models.CASCADE)
    last_read_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.function_name}"
