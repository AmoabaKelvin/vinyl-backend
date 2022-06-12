from django.db.models.signals import pre_save
from django.dispatch import receiver

from . import utils
from .models import Song


@receiver(pre_save, sender=Song)
def add_track_duration_to_song(sender, instance, **kwargs):
    instance.track_duration = utils.calculate_song_duration(instance.audio_file)
