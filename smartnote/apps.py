from django.apps import AppConfig


class SmartnoteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'smartnote'
    def ready(self):
        import smartnote.signals