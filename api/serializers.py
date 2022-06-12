from accounts.models import CustomUser
from rest_framework import serializers
from song.models import Song


class SongSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    artist = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        model = Song
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'songs')
