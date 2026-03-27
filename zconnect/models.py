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

class Company(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    appid = models.CharField(max_length=255)
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
    avatar = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
      
class ZUsers(models.Model):
    oauth = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.OneToOneField(ZProfile, on_delete=models.CASCADE, null=True, blank=True)
    company = models.OneToOneField(Company, on_delete=models.CASCADE, null=True, blank=True)
    zaloid = models.CharField(max_length=128)
    zalonumber = models.CharField(max_length=128)
    isvalidated = models.BooleanField(default=False)
    isadmin = models.BooleanField(default=False)
    isdevelopment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.oauth:
            alphabet = string.ascii_letters + string.digits
            random_password = ''.join(secrets.choice(alphabet) for i in range(16))
            user = User.objects.create(
                username=f"zalo_login_{self.zaloid}",
                password=random_password,
            )
            self.oauth_user = user
        super().save(*args, **kwargs)
    def __str__(self):
        return self.zaloid
    class Meta:
        ordering = ["-id"]
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
    picture = models.FileField(upload_to='note_pictures/', blank=True, null=True)
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
    def reduce_image_size(self, picture):
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
    def save(self, *args, **kwargs):
        if self.picture:
            self.picture = self.reduce_image_size(self.picture)
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