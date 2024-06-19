from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    def ready(self):
        from myapp.tasks import clear_media_periodically
        # Set interval to the desired number of hours converted to seconds (e.g., every 6 hours)
        clear_media_periodically(24*60*60)
