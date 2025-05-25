from .a import *
from .company import *

class AdvanceType(models.Model): # loại phê duyệt
    typecode = models.CharField(max_length=100, unique=True)
    need_operator = models.BooleanField(default=False) # người thụ hưởng là công nhân
    need_approver = models.BooleanField(default=False) # cần phê duyệt
    color = models.CharField(max_length=10, null=True,blank=True, default='#999999')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                 null=True,blank=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.id}"
    
class AdvanceReasonType(models.Model): # phân loại nguyên nhân phê duyệt
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True,blank=True)
    typename = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.id}"
      
class AdvanceRequest(models.Model): # phê duyệt
    STATUS_CHOICES = [
        ('cancel', 'Hủy bỏ'),
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]
    PAYMENT_CHOICES = [
        ('not', 'Chưa giải ngân'),
        ('done', 'Đã giải ngân'),
    ]
    RETRIEVE_CHOICES = [
        ('not', 'Chưa thu hồi'),
        ('done', 'Đã thu hồi'),
    ]
    PAY_CHOICES = [
        ('bank', 'Chuyển khoản'),
        ('money', 'Tiền mặt'),
    ]
    PAYER_CHOICES = [
        ('other', 'Người khác'),
        ('opertor', 'Người lao động'),
        ('staff', 'Người tạo yêu cầu'),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True,blank=True)
    requester = models.ForeignKey(CompanyStaff, on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="advance_requests")
    requesttype = models.ForeignKey(AdvanceType, on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="advance_type")
    # người phê duyệt
    approver = models.ForeignKey(CompanyStaff, on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="advance_approver")
    # người thụ hưởng
    operator = models.ForeignKey(CompanyOperator, on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="advance_operator")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.ForeignKey(AdvanceReasonType, on_delete=models.SET_NULL,null=True,blank=True)
    hinhthucThanhtoan = models.CharField(max_length=10, choices=PAY_CHOICES, default='bank')
    nguoiThuhuong = models.CharField(max_length=10, choices=PAYER_CHOICES, default='opertor')
    khacCtk = models.CharField(max_length=100, null=True,blank=True)
    khacNganhang = models.CharField(max_length=10, null=True,blank=True)
    khacStk = models.CharField(max_length=20, null=True,blank=True)
    
    request_date = models.DateField(null=True,blank=True)
    comment = models.TextField(null=True,blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='not')
    retrieve_status = models.CharField(max_length=15, choices=RETRIEVE_CHOICES, default='not')
    
    request_code = models.CharField(max_length=15, unique=True, blank=True, null=True)  # Trường mã yêu cầu

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
    def generate_request_code(self):
        """Tạo mã yêu cầu PDOC-[random 10 ký tự]"""
        return 'PDOC-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    def save(self, *args, **kwargs):
        if not self.request_code:
            self.request_code = self.generate_request_code()
            while AdvanceRequest.objects.filter(request_code=self.request_code).exists():
                self.request_code = self.generate_request_code()  # Nếu đã tồn tại, tạo lại
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.amount} - {self.get_status_display()}"   
    
class AdvanceRequestHistory(models.Model): # phân loại nguyên nhân phê duyệt
    ACTION_CHOICES = [
        ('update', 'Cập nhập'),
        ('edit', 'Chỉnh sửa'),
        ('create', 'Tạo mới'),
        ('cancel', 'Hủy bỏ'),
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]
    request = models.ForeignKey(AdvanceRequest, on_delete=models.CASCADE, null=True,blank=True)
    user = models.ForeignKey(CompanyStaff, on_delete=models.SET_NULL,
                                 null=True,blank=True, 
                                 related_name="advance_history_approver")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, default='pending')
    old_data = models.JSONField(null=True,blank=True)
    new_data = models.JSONField(null=True,blank=True)
    comment = models.TextField(null=True,blank=True,max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.id}"
          