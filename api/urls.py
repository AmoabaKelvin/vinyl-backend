from django.urls import include, path

from . import views

urlpatterns = [
    path('songs/', views.song_list_or_create_song),
    path('songs/<int:id>', views.retrieve_particular_song),
    path('users/<int:id>', views.retrieve_particular_user),
    path('songs/search/<str:song_name>', views.search_song),
    path('accounts/', include('accounts.urls')),
    # redirect all payment request to the checkout app
    path('checkout/', include('checkout.urls')),
]
