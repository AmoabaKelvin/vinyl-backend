from accounts.models import CustomUser
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from song.models import Song

from api.utils import return_structured_data

from .permissions import UserIsArtistOrReadOnly
from .serializers import CustomUserSerializer, SongSerializer


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated, UserIsArtistOrReadOnly])
def song_list_or_create_song(request):
    """
    List all songs, or create a new song.
    """
    if request.method == 'GET':
        songs = Song.objects.all()
        serializer = SongSerializer(songs, many=True)
        return Response(return_structured_data('success', serializer.data, ''))

    if request.method == 'POST':
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(artist=request.user)
            return Response(return_structured_data('success', serializer.data, ''))
        serializer_error = (
            f"missing field: {','.join(list(serializer.errors.keys()))}"
        )
        return Response(
            return_structured_data('failure', serializer.data, serializer_error)
        )


@api_view(['GET'])
def retrieve_particular_song(request, id: int):
    """
    Retrieve a particular song.
    """
    song = get_object_or_404(Song, id=id)
    serializer = SongSerializer(song)
    return Response(return_structured_data('success', serializer.data, ''))


@api_view(['GET'])
def retrieve_particular_user(request, id: int):
    """
    Retrieve a particular user.
    """
    user = get_object_or_404(CustomUser, id=id)
    serializer = CustomUserSerializer(user)
    return Response(return_structured_data('success', serializer.data, ''))


@api_view(['GET'])
def search_song(request, song_name: str):
    """
    Search for a song by name.
    """
    songs = Song.objects.filter(title__icontains=song_name)
    serializer = SongSerializer(songs, many=True)
    return Response(return_structured_data('success', serializer.data, ''))
