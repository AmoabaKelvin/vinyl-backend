from django.urls import path

from . import views

urlpatterns = [
    path('buy/<int:song_id>', views.buy_song, name='buy_song'),
    path('balance', views.retrieve_account_balance, name='balance'),
    path('account/info', views.retrieve_account_info, name='account'),
    path('account/update', views.update_account_info, name='account_update'),
    path('payout', views.request_payout, name='payout'),
    path('refund/<int:song_id>', views.request_payment_refund, name='request_refund'),
    path(
        'artist/history',
        views.retrieve_artist_transaction_history,
        name='artist_history',
    ),
    path(
        'customer/history',
        views.retrieve_customer_transaction_history,
        name='customer_history',
    ),
    path('done', views.display_thank_you, name='done'),
]
