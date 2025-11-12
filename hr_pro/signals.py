from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=HRUser)
def create_oauth_user(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        UserConfigs.objects.get_or_create(user=instance)