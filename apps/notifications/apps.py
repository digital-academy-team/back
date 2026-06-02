from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'

    def ready(self):
        # Wire up the post_save signal that turns assignment submissions /
        # gradings into Notification rows. Imported here so it only registers
        # once the app registry is ready.
        from . import signals  # noqa: F401
