from django.db import models
from django.contrib.auth.models import User
from .a import *

class image_safe(models.Model): # Phân loại công ty
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    size = models.TextField(null=True, blank=True)
    width = models.TextField(null=True, blank=True)
    height = models.TextField(null=True, blank=True)
    fileType = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
      
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    public = models.BooleanField(default=True)
    full_name = models.CharField(max_length=255, blank=True)
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
      
class CompanyType(models.Model): # Phân loại công ty
    code = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # người tạo
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        verbose_name = "Company Types"
        verbose_name_plural = "Company Types"
    def __str__(self):
        return f"{self.name}"
    
class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # người sở hữu
    companyType = models.ForeignKey(CompanyType, on_delete=models.SET_NULL, null=True, blank=True)
    avatar= models.ForeignKey(image_safe, on_delete=models.SET_NULL, null=True, blank=True, related_name="cpn_avatar")
    wallpaper= models.ForeignKey(image_safe, on_delete=models.SET_NULL, null=True, blank=True, related_name="cpn_wallpaper")
    key = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    fullname = models.TextField(null=True, blank=True)
    companyCode = models.CharField(max_length=200, null=True, blank=True)
    operatorCode = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    addressDetails = models.JSONField(null=True, blank=True)
    taxCode = models.CharField(max_length=200, null=True, blank=True)
    hotline = models.CharField(max_length=200, null=True, blank=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    isValidate = models.BooleanField(default=False, null=True, blank=True)
    isOA = models.BooleanField(default=False, null=True, blank=True)
    shortDescription = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    zalo = models.CharField(max_length=200, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    instagram = models.CharField(max_length=200, null=True, blank=True)
    tiktok = models.CharField(max_length=200, null=True, blank=True)
    facebook = models.CharField(max_length=200, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        verbose_name = "Company"
        verbose_name_plural = "Company"
    def __str__(self):
        return f"{self.name}"
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = uuid.uuid4().hex.upper()
        super(Company, self).save(*args, **kwargs)
         
class CompanyDepartment(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        verbose_name = "Company Departments"
        verbose_name_plural = "Company Departments"
    def __str__(self):
        return f"{self.name}"    
      
class CompanyPossition(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(CompanyDepartment, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        verbose_name = "Company Possitions"
        verbose_name_plural = "Company Possitions"
    def __str__(self):
        return f"{self.name}"
     
class CompanyUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employee_accounts')
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('company', 'username')
        verbose_name = "Company Accounts"
        verbose_name_plural = "Company Accounts"
    def save(self, *args, **kwargs):
        if not self.username or not self.password:
            raise ValidationError("Username và password không được để trống.")
        if not self.password.startswith('pbkdf2_sha256$'):  # Kiểm tra xem mật khẩu đã mã hóa chưa
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.username} ({self.company.key})"
    
class CompanyCustomer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    fullname = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    hotline = models.CharField(max_length=200, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        unique_together = ('company', 'name')
        verbose_name = "Company Customers"
        verbose_name_plural = "Company Customers"
    def __str__(self):
        return f"{self.name}"
    
# Bảng lưu hợp đồng giữa Company và Customer
class Contract(models.Model):
    company_customer = models.ForeignKey(CompanyCustomer, on_delete=models.CASCADE, related_name='contracts')
    contract_number = models.CharField(max_length=100, unique=True)  # Số hợp đồng
    title = models.CharField(max_length=255, null=True, blank=True)  # Tiêu đề hợp đồng
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)  # Mô tả hợp đồng
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Hợp đồng"
        verbose_name_plural = "Hợp đồng"
    def __str__(self):
        return f"Contract {self.contract_number} with {self.company_customer.name}"
# Bảng lưu báo giá, liên kết với hợp đồng hoặc trực tiếp khách hàng
class Quotation(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='quotations', null=True, blank=True)
    company_customer = models.ForeignKey(CompanyCustomer, on_delete=models.CASCADE, related_name='quotations')
    quotation_number = models.CharField(max_length=100, unique=True)  # Số báo giá
    description = models.TextField(null=True, blank=True)  # Mô tả báo giá
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Giá trị báo giá
    valid_from = models.DateField(null=True, blank=True)   # Bắt đầu có hiệu lực
    valid_until = models.DateField(null=True, blank=True)  # Hết hiệu lực
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Báo giá"
        verbose_name_plural = "Báo giá"
    def __str__(self):
        return f"Quotation {self.quotation_number} for {self.company_customer.name}"
    
    def clean(self):
        if not self.start_date:
            raise ValidationError("Hợp đồng phải có ngày bắt đầu (start_date).")

        # Tìm hợp đồng khác của cùng khách hàng có end_date chồng lấn hoặc chưa có end_date
        overlapping_contracts = Contract.objects.filter(
            company_customer=self.company_customer,
            start_date__lte=self.start_date,
        ).exclude(pk=self.pk)

        for contract in overlapping_contracts:
            # Nếu hợp đồng cũ chưa có end_date hoặc end_date >= start_date hợp đồng mới thì báo lỗi (hoặc xử lý)
            if contract.end_date is None or contract.end_date >= self.start_date:
                # Nếu chưa có end_date, sẽ update end_date thành trước start_date hợp đồng mới
                if contract.end_date is None:
                    contract.end_date = self.start_date - timedelta(days=1)
                    contract.save()
                else:
                    raise ValidationError(
                        f"Hợp đồng {contract.contract_number} đang chồng lấn thời gian với hợp đồng mới."
                    )
    def save(self, *args, **kwargs):
        self.clean()  # gọi check trước khi save
        super().save(*args, **kwargs)
    
class CompanyStaff(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    cardID = models.CharField(max_length=200, null=True, blank=True) # mã NV
    user = models.OneToOneField(CompanyUser, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(CompanyDepartment, on_delete=models.SET_NULL, null=True, blank=True) # bộ phận
    possition = models.ForeignKey(CompanyPossition, on_delete=models.SET_NULL, null=True, blank=True) # vị trí
    isActive = models.BooleanField(default=False, null=True, blank=True) # nghỉ việc
    isSuperAdmin = models.BooleanField(default=False, null=True, blank=True)
    isAdmin = models.BooleanField(default=False, null=True, blank=True)
    isSystem = models.BooleanField(default=False, null=True, blank=True)
    isBan = models.BooleanField(default=False, null=True, blank=True) # bị ban
    isOnline = models.BooleanField(default=False, null=True, blank=True) # online trên app
    isValidate = models.BooleanField(default=False, null=True, blank=True) # được phê duyệt
    managerCustomer=models.ManyToManyField(CompanyCustomer,blank=True)
    socket_id = models.CharField(max_length=200, null=True, blank=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        unique_together = ('company', 'cardID')
        verbose_name = "Company Staff"
        verbose_name_plural = "Company Staff"
    def __str__(self):
        username = self.user.username if self.user else "NoUser"
        return f"{self.cardID}_{username}_{self.company}"
    
class CompanyStaffProfile(models.Model):
    staff = models.OneToOneField(CompanyStaff, on_delete=models.CASCADE, related_name='profile')
    public = models.BooleanField(default=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    nick_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Nam'), ('female', 'Nữ')], blank=True)
    avatar = models.URLField(blank=True, null=True)
    avatar_base64 = models.TextField(blank=True, null=True)  # <--- thêm dòng này
    date_of_birth = models.DateField(null=True, blank=True)
    
    nganhang= models.CharField(max_length=200, null=True, blank=True)
    so_taikhoan= models.CharField(max_length=200, null=True, blank=True)
    chu_taikhoan= models.CharField(max_length=200, null=True, blank=True)
    zalo= models.CharField(max_length=200, null=True, blank=True)
    facebook= models.CharField(max_length=200, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.staff.cardID}_{self.staff.user.username}"
    
class CompanyConfig(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)

    # sửa thông tin người lao động
    editop_active = models.BooleanField(default=True)
    staff_can_update_op_info = models.BooleanField(default=True)
    admin_can_update_op_info = models.BooleanField(default=True)
    staffs_can_update_op_info = models.ManyToManyField(
        CompanyStaff,blank=True,related_name='staff_can_update_op_info'
    )
    # lịch sử đi làm
    staff_can_update_op_work = models.BooleanField(default=True)
    admin_can_update_op_work = models.BooleanField(default=True)
    staffs_can_update_op_work = models.ManyToManyField(
        CompanyStaff,blank=True,related_name='staff_can_update_op_work'
    )
    # báo ứng
    baoung_active = models.BooleanField(default=True)
    baoung_active_time = models.BooleanField(default=False)
    baoung_active_start = models.DateTimeField(blank=True,null=True)
    baoung_active_end = models.DateTimeField(blank=True,null=True)
    # phê duyệt
    approve_active = models.BooleanField(default=True)
    admin_can_payout = models.BooleanField(default=False)
    admin_can_approve = models.BooleanField(default=False)
    staff_approve_admin = models.ManyToManyField(
        CompanyStaff,blank=True, 
        related_name='staff_approve_admin'
    )
    staff_can_approve = models.ManyToManyField(
        CompanyStaff,blank=True, 
        related_name='staff_can_approve'
    )
    staff_can_payout = models.ManyToManyField(
        CompanyStaff,blank=True, 
        related_name='staff_can_payout'
    )
    staff_can_approve_and_payout = models.ManyToManyField(
        CompanyStaff,blank=True, 
        related_name='staff_can_approve_and_payout'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        verbose_name = "Company Configurations"
        verbose_name_plural = "Company Configurations"
    def __str__(self):
        return f"{self.id}"
    
class CompanyStaffHistoryFunction(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        verbose_name = "Company Staff Action History Functions"
        verbose_name_plural = "Company Staff Action History Functions"
    def __str__(self):
        return f"{self.name}"
    
class CompanyStaffHistoryAction(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        verbose_name = "Company Staff Action Historys"
        verbose_name_plural = "Company Staff Action Historys"
    def __str__(self):
        return f"{self.name}"
    
class CompanyStaffHistory(models.Model):
    staff = models.ForeignKey(CompanyUser, on_delete=models.SET_NULL, null=True, blank=True)
    function = models.ForeignKey(CompanyStaffHistoryFunction, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.ForeignKey(CompanyStaffHistoryAction, on_delete=models.SET_NULL, null=True, blank=True)
    ip_action=models.GenericIPAddressField(null=True,blank=True)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    title= models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    isHidden = models.BooleanField(default=False, null=True, blank=True)
    isSended = models.BooleanField(default=False, null=True, blank=True)
    isReceived = models.BooleanField(default=False, null=True, blank=True)
    isReaded = models.BooleanField(default=False, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        verbose_name = "Company Staff History"
        verbose_name_plural = "Company Staff History"
    def __str__(self):
        return f"{self.staff.username}"
    
class CompanyVendor(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_sub = models.BooleanField(default=False, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    subname = models.CharField(max_length=200, null=True, blank=True)
    fullname = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    hotline = models.CharField(max_length=200, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        unique_together = ('company', 'name', 'subname')
        verbose_name = "Company Vendors"
        verbose_name_plural = "Company Vendors"
    def __str__(self):
        return f"{self.name}"
    
class CompanyOperator(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    ma_nhanvien= models.CharField(max_length=200, null=True, blank=True)
    ngay_phongvan = models.DateField(default=timezone.now,null=True, blank=True)
    
    sdt= models.CharField(max_length=15, null=True, blank=True)
    ho_ten= models.CharField(max_length=200, null=True, blank=True)
    gioi_tinh= models.CharField(max_length=200, null=True, blank=True)
    ten_goc= models.CharField(max_length=200, null=True, blank=True)
    so_cccd= models.CharField(max_length=200, null=True, blank=True)
    ngaysinh= models.DateField(null=True, blank=True)
    diachi= models.CharField(max_length=200, null=True, blank=True)
    quequan= models.CharField(max_length=200, null=True, blank=True)
    
    avatar= models.TextField(null=True, blank=True)
    cccd_front= models.TextField(null=True, blank=True)
    cccd_back= models.TextField(null=True, blank=True)
    
    trangthai= models.CharField(max_length=200, null=True, blank=True)
    nganhang= models.CharField(max_length=200, null=True, blank=True)
    so_taikhoan= models.CharField(max_length=200, null=True, blank=True)
    chu_taikhoan= models.CharField(max_length=200, null=True, blank=True)
    ghichu_taikhoan= models.CharField(max_length=200, null=True, blank=True)
    ghichu= models.CharField(max_length=200, null=True, blank=True)
    import_raw= models.JSONField(max_length=9999, null=True, blank=True)
    
    nguoituyen = models.ForeignKey(CompanyStaff, on_delete=models.SET_NULL, null=True, blank=True,related_name="companyOP_nguoituyen")
    vendor = models.ForeignKey(CompanyVendor, on_delete=models.SET_NULL, null=True, blank=True,related_name="companyOP_vendor")
    congty_danglam = models.ForeignKey(CompanyCustomer, on_delete=models.SET_NULL, null=True, blank=True)
    nhachinh = models.ForeignKey(CompanyVendor, on_delete=models.SET_NULL, null=True, blank=True,related_name="companyOP_nhachinh")
    nguoibaocao = models.ForeignKey(CompanyStaff, on_delete=models.SET_NULL, null=True, blank=True,related_name="companyOP_nguoibaocao")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        verbose_name = "Operator 1 List"
        verbose_name_plural = "Operator 1 List"
        unique_together = [
            ('company', 'ma_nhanvien'),
            ('so_cccd', 'nhachinh'),
        ]
    def save(self, *args, **kwargs):
        if not self.ma_nhanvien:
            self.ma_nhanvien = f"RANDOM_{uuid.uuid4().hex.upper()[:18]}"
        super(CompanyOperator, self).save(*args, **kwargs)
    def __str__(self):
        return f"{self.ma_nhanvien}"

class OperatorUpdateHistory(models.Model):
    operator = models.ForeignKey(CompanyOperator, on_delete=models.CASCADE, related_name="history")
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    changed_by = models.ForeignKey(CompanyStaff, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Operator 2 Update History"
        verbose_name_plural = "Operator 2 Update Histories"
        ordering = ['-changed_at']

class OperatorWorkHistory(models.Model):
    operator = models.ForeignKey(CompanyOperator, on_delete=models.CASCADE , related_name="work_histories")
    customer = models.ForeignKey(CompanyCustomer, on_delete=models.CASCADE, related_name="operator_histories")
    vendor = models.ForeignKey(CompanyVendor, on_delete=models.SET_NULL, null=True, blank=True, related_name="operator_vendor")
    nhachinh = models.ForeignKey(CompanyVendor, on_delete=models.SET_NULL, null=True, blank=True, related_name="operator_nhachinh")
    nguoituyen = models.ForeignKey(CompanyStaff, on_delete=models.SET_NULL, null=True, blank=True,related_name="companyHIS_nguoituyen")
    so_cccd= models.CharField(max_length=200, null=True, blank=True)
    anh_cccd_front= models.TextField(null=True, blank=True)
    anh_cccd_back= models.TextField(null=True, blank=True)
    ma_nhanvien= models.CharField(max_length=200, null=True, blank=True)
    ho_ten= models.CharField(max_length=200, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)  # Thời gian bắt đầu làm việc
    end_date = models.DateField(null=True, blank=True)    # Thời gian kết thúc làm việc
    vitri = models.CharField(max_length=200, null=True, blank=True) # vị trí làm việc
    notes = models.TextField(null=True, blank=True)           # Ghi chú thêm nếu cần
    reason = models.TextField(null=True, blank=True)           # Ghi chú thêm nếu cần
    noihopdong = models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True,related_name="next_histories")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']  # Sắp xếp theo thời gian bắt đầu mới nhất
        verbose_name = "Operator 3 Working History"
        verbose_name_plural = "Operator 3 Working Histories"

    def __str__(self):
        return f"{self.operator} -> {self.customer} ({self.start_date} - {self.end_date})"


class Company_Salary_type(models.Model): # Phân loại lương (Lương cơ bản)
    action_choice=[('+', 'Cộng'), ('-', 'Trừ'), ('*', 'Nhân'), ('/', 'Chia')]
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    # Kế thừa từ một loại lương nữa bằng 1 phép tính
    parent = models.ForeignKey('self',on_delete=models.SET_NULL, null=True, blank=True)
    parent_action = models.CharField(max_length=200, null=True, blank=True)
    parent_action_target = models.FloatField(default=1, null=True, blank=True)
    parent_action_target_parent = models.ForeignKey('self',
        related_name="salary_type_target",
        on_delete=models.SET_NULL, 
        null=True, blank=True
    )
    
    # Loại lương
    name = models.CharField(max_length=200, null=True, blank=True)
    shortname = models.CharField(max_length=200, null=True, blank=True)
    descriptions = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
    # Ví dụ: Lương cơ bản, 
    # Lương tăng ca = Lương cơ bản * 1.5, 
    # Lương nghỉ 70% = Lương cơ bản * 0.7,....
    
class Company_Hour_type(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    heso = models.IntegerField(default=100, null=True, blank=True)
    shortname = models.CharField(max_length=200, null=True, blank=True)
    descriptions = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.name}"
    
class CompanyCustomer_salary(models.Model):
    customer = models.ForeignKey(CompanyCustomer, on_delete=models.CASCADE,null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True, blank=True)
    dongia = models.IntegerField(default=0, null=True, blank=True)
    ngayapdung = models.DateField(auto_now=True)

    staff = models.ForeignKey(CompanyStaff, on_delete=models.SET_NULL, 
                                   null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.id}"
    
class CompanyOperator_workHours(models.Model):
    operator = models.ForeignKey(CompanyOperator, on_delete=models.CASCADE,null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True, blank=True)
    
    ngaylamviec = models.DateField()
    is_single = models.BooleanField(default=True) # Ngày lẻ
    denngay = models.DateField(null=True, blank=True)
    heso = models.FloatField(default=0, null=True, blank=True)
    sogio = models.FloatField(default=0, null=True, blank=True)
    staff = models.ForeignKey(CompanyStaff, on_delete=models.SET_NULL, 
                                   null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.denngay:
            self.is_single=False # nếu mà là giải ngày thì single = False
        super(CompanyOperator, self).save(*args, **kwargs)
        
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f"{self.id}"
    