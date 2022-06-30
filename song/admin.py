from typing import Sequence

from django.contrib import admin

from .models import Song


class SongAdmin(admin.ModelAdmin):
    list_display: Sequence[str] = [
        'artist',
        'title',
        'genre',
        'producer',
        'release_date',
        'created_at',
        'updated_at',
    ]
    list_filter: Sequence[str] = [
        'artist',
        'genre',
        'producer',
        'writer',
        'release_date',
        'created_at',
        'updated_at',
    ]
    search_fields: Sequence[str] = [
        'artist',
        'title',
        'genre',
        'producer',
        'featured_artists',
        'writer',
        'release_date',
        'created_at',
        'updated_at',
    ]
    readonly_fields: Sequence[str] = ['created_at', 'updated_at']


admin.site.register(Song, SongAdmin)
