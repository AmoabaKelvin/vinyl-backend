from accounts.models import CustomUser
from django.db import models


class Song(models.Model):
    """
    Model for a song
    """

    artist = models.ForeignKey(
        to=CustomUser, on_delete=models.CASCADE, related_name='songs'
    )
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    producer = models.CharField(max_length=150)
    featured_artists = models.CharField(max_length=255, blank=True)
    writer = models.CharField(max_length=150, blank=True)
    release_date = models.DateField()
    cover_art = models.ImageField(upload_to='cover_arts/', blank=True)
    audio_file = models.FileField(upload_to='audio_files/')
    # the track duration will be calculated based on the audio file
    track_duration = models.CharField(max_length=8, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
