from django.urls import path

from . import views

urlpatterns = [
    path('buy/<int:song_id>', views.buy_song, name='buy_song'),
    path('balance', views.retrieve_account_balance, name='balance'),
]
