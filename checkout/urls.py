from django.urls import path

from . import views

urlpatterns = [
    path('buy/<int:song_id>', views.buy_song, name='buy_song'),
    path('balance', views.retrieve_account_balance, name='balance'),
    path('account/info', views.retrieve_account_info, name='account'),
    path('account/update', views.update_account_info, name='account_update'),
    path('payout', views.request_payout, name='payout'),
    # path('account/delete', views.delete_account, name='account_delete'),
    path('done', views.display_thank_you, name='done'),
]
