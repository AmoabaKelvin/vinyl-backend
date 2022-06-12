from django.apps import AppConfig


class SongConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'song'

    def ready(self) -> None:
        from . import signals
