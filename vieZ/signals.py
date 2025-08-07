from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from .models import *
import os
import json

@receiver(post_save, sender=Users)
def create_oauth_user(sender, instance, created, **kwargs):
    if created and not instance.oauth_user:
        # create oauth user
        oauth_username = f"smartuser_{instance.username}"
        password = instance.password
        user = User.objects.create(
            username=oauth_username,
            password=make_password(password),
        )
        instance.oauth_user = user
        instance.save()
        # create user profile and config
        free_plan,_ = UserPlan.objects.get_or_create(name="Free")
        UserProfile.objects.create(user=instance)
        UserConfigs.objects.create(user=instance,plan=free_plan)
def load_default_config():
    file_path = os.path.join(os.path.dirname(__file__), 'appcfs.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
@receiver(post_save, sender=UserApps)
def create_default_app_config(sender, instance, created, **kwargs):
    if created:
        default_configs = load_default_config()
        UserAppsConfigs.objects.create(
            app=instance,
            name="Cấu hình mặc định",
            is_active=True,
            configs=default_configs
        )