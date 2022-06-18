import ast
import os

import stripe
from api.utils import return_structured_data
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from profiles.models import ArtistCustomerProfile, NormalCustomerProfile

# from profiles.models import ArtistCustomerProfile
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from song.models import Song

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def buy_song(request, song_id):
    """
    Process the payment for a song
    Args:
        song_id: id of the song to be purchased
    Returns:
        Response: response object
    """
    song = get_object_or_404(Song, id=song_id)
    # get the song data from the song object.
    # the obtained data will be used to make the Payment
    song_price = song.price
    song_artist = song.artist
    song_artist_connect_id = ArtistCustomerProfile.objects.get(
        artist=song_artist
    ).artistid
    song_price_for_stripe = int(song_price * 100)
    # start processing payment
    payment_intent = stripe.PaymentIntent.create(
        amount=song_price_for_stripe,
        currency='usd',
        description=f"Payment for song {song.title}-{song.artist}",
        application_fee_amount=int(
            song_price_for_stripe * 0.03
        ),  # 3% of the song price
        transfer_data={
            # the destination represents the account that the money will be
            # transferred to, in this case, the artist's account
            'destination': song_artist_connect_id,
        },
        automatic_payment_methods={'enabled': True},
    )
    return Response(
        return_structured_data('success', payment_intent.client_secret, ''),
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def retrieve_account_balance(request):
    """
    Retrieve the account balance of an artist
    """
    # get the artist customer profile
    artist_customer_profile = ArtistCustomerProfile.objects.get(artist=request.user)
    # get the account balance
    try:
        response: dict = stripe.Balance.retrieve(
            stripe_account=artist_customer_profile.artistid
        )
    except Exception as e:
        response = {'error': 'error retrieving account balance'}
        return Response(return_structured_data('failure', response, ''))
    # if no error, return the account balance, specifically the
    # available_balance and the pending balance.
    # https://stripe.com/docs/api/balance/balance_object
    available_balance = response['available'][0]['amount']
    pending_balance = response['pending'][0]['amount']
    response_data = {
        'available_balance': available_balance,
        'pending_balance': pending_balance,
    }
    return Response(return_structured_data('success', response_data, ''))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def retrieve_account_info(request):
    """
    Retrieve account information for a user(artist).
    """
    # get the customer profile
    artist_profile = ArtistCustomerProfile.objects.get(artist=request.user)
    artist_stripe_account_id = artist_profile.artistid
    try:
        response: dict = stripe.Account.retrieve(artist_stripe_account_id)
    except Exception as e:
        return Response(
            return_structured_data('failure', '', 'Failed to retrieve account info')
        )
    return Response(return_structured_data('success', response, ''))


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_account_info(request):
    """
    Update the account information of an artist
    """
    try:
        stripe_data = ast.literal_eval(request.data['stripe_data'])
    except:
        return Response(
            return_structured_data('failure', '', 'Could not parse stripe_data')
        )
    artist = ArtistCustomerProfile.objects.get(artist=request.user)
    artist_stripe_account_id = artist.artistid
    try:
        response: dict = stripe.Account.modify(
            artist_stripe_account_id,
            business_type="individual",
            metadata=stripe_data,
        )
    except Exception as e:
        return Response(
            return_structured_data('failure', '', 'Failed to update account info')
        )
    return Response(return_structured_data('success', response, ''))


@api_view(['GET'])
def display_thank_you(request):
    """
    Display the thank you page
    """
    return Response(
        return_structured_data('success', '', 'Thank you for your purchase')
    )


# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def delete_account(request):
#     """
#     Delete the account of an artist
#     """
#     if request.user.is_artist:
#         artist = ArtistCustomerProfile.objects.get(artist=request.user)
#         artist_stripe_account_id = artist.artistid
#         response: dict = stripe.Account.delete(artist_stripe_account_id)
#         artist.delete()
#     customer = NormalCustomerProfile.objects.get(customer=request.user)
#     customer_id = customer_id.customerid
#     try:
#         response: dict = stripe.Account.delete(customer_id)
#         customer.delete()
#     except Exception as e:
#         return Response(
#             return_structured_data('failure', '', 'Failed to delete account')
#         )
#     return Response(
#         return_structured_data('success', response, ''), status=status.HTTP_200_OK
#     )
