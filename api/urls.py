from django.urls import include, path

from . import views

urlpatterns = [
    # path('songs/', views.SongList.as_view()),
    path('songs/', views.song_list_or_create_song),
    # path('songs/<int:id>', views.SongDetail.as_view()),
    path('songs/<int:id>', views.retrieve_particular_song),
    # path('songs/<int:id>', views.retrieve_particular_song),
    path('users/<int:id>', views.UserDetailView.as_view()),
    # redirect all requests to api/accounts to the accounts app
    path('accounts/', include('accounts.urls')),
]
