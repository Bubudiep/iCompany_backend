from .a import *
from .company import Company, CompanyStaff, CompanyDepartment, CompanyPossition

class Permission(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Tên quyền
    fullname = models.CharField(max_length=200,null=True, blank=True)  # Tên quyền
    description = models.TextField(null=True, blank=True)  # Mô tả quyền
    min_company_level = models.PositiveIntegerField(default=1)  # Level tối thiểu của công ty để sử dụng quyền
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['-id']

    def __str__(self):
        return f"{self.name}"
    
class PermissionType(models.Model):
    name = models.CharField(max_length=20, unique=True)  # Ví dụ: view, edit, delete, ...
    display_name = models.CharField(max_length=50)  # Ví dụ: Xem, Sửa, Xóa, ...

    class Meta:
        verbose_name = "Permission Type"
        verbose_name_plural = "Permission Types"
    def __str__(self):
        return self.display_name

class TargetType(models.Model):
    name = models.CharField(max_length=20, unique=True)  # Ví dụ: me, position, department, all
    display_name = models.CharField(max_length=50)  # Ví dụ: Cá nhân, Vị trí, Phòng ban, Tất cả
    class Meta:
        verbose_name = "Permission Type Target"
        verbose_name_plural = "Permission Types Target"
    def __str__(self):
        return self.display_name
    
class CompanyPermission(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='company_permissions')
    permission_types = models.ManyToManyField(PermissionType, blank=True, related_name='company_permissions')  # Thay permission_type
    target_types = models.ManyToManyField(TargetType, blank=True, related_name='company_permissions')  # Thay target_type
    is_active = models.BooleanField(default=True)  # Quyền có đang được kích hoạt không
    assigned_by = models.ForeignKey(CompanyStaff, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_permissions')  # Ai cấp quyền
    assigned_at = models.DateTimeField(default=timezone.now)

    # Áp dụng quyền cho nhân viên, phòng ban, vị trí
    applicable_staff = models.ManyToManyField(CompanyStaff, related_name='company_permissions', blank=True)
    applicable_departments = models.ManyToManyField(CompanyDepartment, related_name='company_permissions', blank=True)
    applicable_positions = models.ManyToManyField(CompanyPossition, related_name='company_permissions', blank=True)

    # Loại trừ nhân viên khỏi quyền này
    excluded_staff = models.ManyToManyField(CompanyStaff, related_name='excluded_permissions', blank=True)
    excluded_departments = models.ManyToManyField(CompanyDepartment, related_name='excluded_permissions', blank=True)

    class Meta:
        verbose_name = "Permission at Company"
        verbose_name_plural = "Permissions at Company"
        unique_together = ('company', 'permission')  # Một công ty chỉ có một Permission duy nhất

    def __str__(self):
        return f"{self.company.name} - {self.permission.name}"

    def get_applicable_sub_permissions(self):
        """Lấy danh sách các SubPermission đang áp dụng"""
        return ", ".join([sub.__str__() for sub in self.sub_permissions.all()]) if self.sub_permissions.exists() else "None"