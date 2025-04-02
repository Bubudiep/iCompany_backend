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
    avatar_base64 = models.TextField(blank=True, null=True)  # <--- thêm dòng này
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
        return f"{self.username} ({self.company.name})"
    
class CompanyStaff(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    cardID = models.CharField(max_length=200, null=True, blank=True) # mã NV
    user = models.OneToOneField(CompanyUser, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(CompanyDepartment, on_delete=models.SET_NULL, null=True, blank=True) # bộ phận
    possition = models.ForeignKey(CompanyPossition, on_delete=models.SET_NULL, null=True, blank=True) # vị trí
    isActive = models.BooleanField(default=False, null=True, blank=True) # nghỉ việc
    isSuperAdmin = models.BooleanField(default=False, null=True, blank=True)
    isAdmin = models.BooleanField(default=False, null=True, blank=True)
    isBan = models.BooleanField(default=False, null=True, blank=True) # bị ban
    isOnline = models.BooleanField(default=False, null=True, blank=True) # online trên app
    isValidate = models.BooleanField(default=False, null=True, blank=True) # được phê duyệt
    socket_id = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-id']
        unique_together = ('company', 'cardID')
        verbose_name = "Company Staff"
        verbose_name_plural = "Company Staff"
    def __str__(self):
        return f"{self.cardID}_{self.user.username}_{self.possition}_{self.company}"
    
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
        return f"{self.staff.name}"
