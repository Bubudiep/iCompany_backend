from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=HRUser)
def create_oauth_user(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        UserConfigs.objects.get_or_create(user=instance)
        
@receiver(post_delete, sender=CompanyImages)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """ Xóa tệp từ hệ thống tập tin khi đối tượng AnhBaiviet bị xóa khỏi DB. """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
@receiver(post_delete, sender=AnhBaiviet)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """ Xóa tệp từ hệ thống tập tin khi đối tượng AnhBaiviet bị xóa khỏi DB. """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)