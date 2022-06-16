from accounts.models import CustomUser
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from song.models import Song

from .serializers import CustomUserSerializer, SongSerializer

# class SongList(ListCreateAPIView):
#     queryset = Song.objects.all()
#     serializer_class = SongSerializer

#     def perform_create(self, serializer):
#         # since no authentication is required in this test, we need to set the
#         # artist field to the root user.
#         serializer.save(artist=CustomUser.objects.first())

#     def list(self, request, *args, **kwargs):
#         # INFO: Override the list method to return a custom json response
#         response = super().list(request, *args, **kwargs)
#         return Response(
#             {
#                 "status": "success" if (response.status_code < 300) else "fail",
#                 "result": response.data,  # return the first element of the list, that is the song dict
#                 "details": "",
#             }
#         )

#     def create(self, request, *args, **kwargs):
#         """
#         Create a model instance of a song or return the error message
#         """
#         serializer = self.get_serializer(data=request.data)
#         # return a custom  json response when the serializer validation fails
#         if not serializer.is_valid():
#             return Response(
#                 {
#                     'status': 'failure',
#                     'result': '',
#                     'details': f"missing field: {','.join([error for error in serializer.errors.keys()])}",
#                 }
#             )
#         response = super().create(request, *args, **kwargs)
#         # return a custom json response when the song is successfully created
#         return Response(
#             {
#                 "status": "success" if (response.status_code < 400) else "fail",
#                 "result": response.data,  # return the first element of the list, that is the song dict
#                 "details": "",
#             }
#         )


# class SongDetail(RetrieveAPIView):
#     lookup_field = 'id'
#     queryset = Song.objects.all()
#     serializer_class = SongSerializer

#     def retrieve(self, request, *args, **kwargs):
#         response = super().retrieve(request, *args, **kwargs)
#         return Response(
#             {
#                 "status": "success",
#                 "result": response.data,  # return the first element of the list, that is the song dict
#                 "details": "",
#             }
#         )


@api_view(['GET', 'POST'])
def song_list_or_create_song(request):
    """
    List all songs, or create a new song.
    """
    if request.method == 'GET':
        songs = Song.objects.all()
        serializer = SongSerializer(songs, many=True)
        return Response(
            {
                'status': 'success',
                'result': serializer.data,
                'details': '',
            }
        )

    if request.method == 'POST':
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(artist=CustomUser.objects.first())
            return Response(
                {
                    'status': 'success',
                    'result': serializer.data,
                    'details': '',
                }
            )
        return Response(
            {
                'status': 'failure',
                'result': '',
                'details': f"missing field: {','.join([error for error in serializer.errors.keys()])}",
            }
        )


@api_view(['GET'])
def retrieve_particular_song(request, id):
    """
    Retrieve a particular song.
    """
    song = get_object_or_404(Song, id=id)
    serializer = SongSerializer(song)
    return Response(
        {
            'status': 'success',
            'result': serializer.data,
            'details': '',
        }
    )


# class UserDetailView(RetrieveAPIView):
#     lookup_field = 'id'
#     queryset = CustomUser.objects.all()
#     serializer_class = CustomUserSerializer


@api_view(['GET'])
def retrieve_particular_user(request, id):
    """
    Retrieve a particular user.
    """
    user = get_object_or_404(CustomUser, id=id)
    serializer = CustomUserSerializer(user)
    return Response(
        {
            'status': 'success',
            'result': serializer.data,
            'details': '',
        }
    )
