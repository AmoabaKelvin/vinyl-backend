from accounts.models import CustomUser
from django.core.files import File
from django.test import TestCase

from ..models import Song


class TestModels(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        CustomUser.objects.create(
            username='test_user',
            email='test@gmail.com',
            password='random123password',
            first_name='test',
            last_name='user',
        )
        Song.objects.create(
            artist=CustomUser.objects.first(),
            title='Test Title',
            genre='Test Genre',
            producer='Test Producer',
            featured_artists='Test Featured Artists',
            writer='Test Writer',
            release_date='2020-01-01',
            cover_art=File(open('song/tests/mock_files/test.jpg', 'rb')),
            audio_file=File(open('song/tests/mock_files/test.mp3', 'rb')),
        )

    def test_song_model_str(self) -> None:
        song = Song.objects.first()
        self.assertEqual(str(song), 'Test Title')

    def test_duration_field_has_value(self) -> None:
        song = Song.objects.first()
        # the logic used to caluclate the track duration is in utils.py
        # the code has been tested on the same file and the result of the duration
        # was 00:04:45
        self.assertEqual(song.track_duration, '00:04:45')
