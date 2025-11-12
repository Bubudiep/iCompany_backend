from django.apps import AppConfig


class HrProConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr_pro'
    def ready(self):
        import hr_pro.signals
