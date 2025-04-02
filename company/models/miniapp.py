from .a import *
from .company import Company

class MiniApp(models.Model):
    appID = models.CharField(max_length=200, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    public = models.BooleanField(default=True)
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
