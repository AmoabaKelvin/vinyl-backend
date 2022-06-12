from accounts.models import CustomUser
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from song.models import Song

from .serializers import CustomUserSerializer, SongSerializer


class SongList(ListCreateAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

    def perform_create(self, serializer):
        # since no authentication is required in this test, we need to set the
        # artist field to the root user.
        serializer.save(artist=CustomUser.objects.first())


class SongDetail(RetrieveAPIView):
    lookup_field = 'id'
    queryset = Song.objects.all()
    serializer_class = SongSerializer


class UserDetailView(RetrieveAPIView):
    lookup_field = 'id'
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
