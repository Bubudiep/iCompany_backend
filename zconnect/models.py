from django.db import models
import secrets
import string
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
import sys
from django.utils.timezone import now

def reduce_image_size(picture):
    img = Image.open(picture)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    max_width = 1280
    max_height = 720
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=80, optimize=True)
    buffer.seek(0)
    file_name = os.path.splitext(picture.name)[0] + ".jpg"
    return ContentFile(buffer.read(), name=file_name)
  
class Company(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    appid = models.CharField(max_length=255)
    hotline = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.code} - {self.name}"

class ZProfile(models.Model):
    name = models.CharField(max_length=255)
    cardid = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    jobtitle = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
      
    def save(self, *args, **kwargs):
        if self.avatar:
            self.avatar = reduce_image_size(self.avatar)
        super().save(*args, **kwargs)
      
class ZUsers(models.Model):
    oauth = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.OneToOneField(ZProfile, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    zaloid = models.CharField(max_length=128,null=True, blank=True)
    zalonumber = models.CharField(max_length=128)
    isvalidated = models.BooleanField(default=False)
    isadmin = models.BooleanField(default=False)
    isdevelopment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.profile:
            self.profile = ZProfile.objects.create(
                name=f"No name",
                phone=self.zalonumber
            )
        if not self.oauth:
            alphabet = string.ascii_letters + string.digits
            random_password = ''.join(secrets.choice(alphabet) for i in range(16))
            self.oauth = User.objects.create(
                username=f"zalo_login_{self.zaloid}",
                password=random_password,
            )
            super().save(*args, **kwargs)
            ZUserNotification.objects.create(
                user=self,
                title="Chào mừng bạn đến với ứng dụng!",
                content="Cảm ơn bạn đã đăng ký tài khoản."
            )
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.zaloid} - {self.zalonumber}"
    class Meta:
        ordering = ["-id"]
class ZUserNotification(models.Model):
    user = models.ForeignKey(ZUsers, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Notification for {self.user.profile.name} at {self.created_at}"
class RequestNoteCategory(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.name} ({self.company.name})"
      
class RequestNote(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    status = models.CharField(
      max_length=50, 
      default='draft',
      choices=[
        ('draft', 'Draft'),
        ('pending', 'Pending'), 
        ('processing', 'Processing'),
        ('completed', 'Completed'), 
        ('rejected', 'Rejected')
      ]
    )
    categories = models.ManyToManyField(RequestNoteCategory, related_name='notes')
    picture = models.ImageField(upload_to='note_pictures/', blank=True, null=True)
    content = models.TextField()
    is_urgent = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    favorited = models.ManyToManyField(ZUsers, related_name='favorite_notes', blank=True)
    pinned = models.ManyToManyField(ZUsers, related_name='pinned_notes', blank=True)
    liked = models.ManyToManyField(ZUsers, related_name='liked_notes', blank=True)
    viewed = models.ManyToManyField(ZUsers, related_name='viewed_notes', blank=True)
    implement =models.ForeignKey(ZUsers, on_delete=models.CASCADE , related_name='implementer')
    author = models.ForeignKey(ZUsers, on_delete=models.CASCADE, related_name='author')
    deadline = models.DateField()

    processing_time = models.DateTimeField(blank=True, null=True)
    completed_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Note for {self.company.name} at {self.created_at}"
    def save(self, *args, **kwargs):
        if self.picture:
            self.picture = reduce_image_size(self.picture)
        super().save(*args, **kwargs)
        
class RequestNoteHistory(models.Model):
    note = models.ForeignKey(RequestNote, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(ZUsers, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"History for {self.note.title} at {self.changed_at}"
      
class RequestNoteComment(models.Model):
    note = models.ForeignKey(RequestNote, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(ZUsers, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Comment by {self.author.name} on {self.note.title}"

class IssueImpact(models.Model):
    name = models.CharField(max_length=250, unique=True)
    vi = models.CharField(max_length=250,null=True,blank=True)
    color = models.CharField(max_length=10, default="#ef4444")
    def __str__(self):
        return self.name
class IssueRickCategories(models.Model):
    name = models.CharField(max_length=250, unique=True)
    color = models.CharField(max_length=10, default="#ef4444")
    def __str__(self):
        return self.name
class IssueCategories(models.Model):
    name = models.CharField(max_length=250, unique=True)
    color = models.CharField(max_length=10, default="#ef4444")
    def __str__(self):
        return self.name
class IssueArea(models.Model):
    name = models.CharField(max_length=250, unique=True)
    vi = models.CharField(max_length=250,null=True,blank=True)
    color = models.CharField(max_length=10, default="#ef4444")
    def __str__(self):
        return self.name
    
class EHSIssue(models.Model):
    Step_choice = [('created', "created"),
                   ('reviewed', "reviewed"), 
                   ('processing', "processing"), 
                   ('closing', "closing"), 
                   ('completed', "completed"), 
                   ('cancelled', "cancelled"), 
                   ('rejected', "rejected")
                ]
    Level_choice = [('low', "Low"), 
                    ('medium', "Medium"), 
                    ('high', "High"), 
                    ('critical', "Critical")]
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    area = models.ManyToManyField(IssueArea,blank=True)
    author = models.ForeignKey(ZUsers, on_delete=models.CASCADE, related_name='ehsissues')
    step = models.CharField(choices=Step_choice, max_length=100, default="created", null=True)
    level = models.CharField(choices=Level_choice, max_length=100, default="low", null=True)
    private = models.BooleanField(default=False)
    impacts = models.ManyToManyField(IssueImpact, blank=True)
    categories = models.ManyToManyField(IssueCategories, blank=True)
    rickcategories = models.ManyToManyField(IssueRickCategories, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-id']
    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
            EHSIssueHistory.objects.create(
                issue=self,
                status=self.step,
                changed_by=self.author,
                changed_at=now()
            )
        
class EHSImage(models.Model):   
    issue = models.ForeignKey('EHSIssue', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='ehs_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Image for {self.issue.title} at {self.created_at}"
    class Meta:
        ordering = ['-id']
    def save(self, *args, **kwargs):
        if self.image:
            self.image = reduce_image_size(self.image)
        super().save(*args, **kwargs)
        
class EHSIssueHistory(models.Model):
    issue = models.ForeignKey(EHSIssue, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(ZUsers, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"History for {self.issue.title} at {self.changed_at}"
      