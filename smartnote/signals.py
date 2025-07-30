from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from .models import *

@receiver(post_save, sender=NoteUser)
def create_oauth_user(sender, instance, created, **kwargs):
    if created and not instance.oauth_user:
        oauth_username = f"smartuser_{instance.username}"
        password = instance.password
        user = User.objects.create(
            username=oauth_username,
            password=make_password(password),
        )
        instance.oauth_user = user
        instance.save()

@receiver(post_save, sender=NoteUser)
def create_related_user_data(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserConfigs.objects.create(user=instance)