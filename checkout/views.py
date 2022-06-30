import ast
import os

import stripe
from api.permissions import UserIsArtistOrError
from api.utils import return_structured_data
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from profiles.models import ArtistCustomerProfile, NormalCustomerProfile
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from song.models import Song

from .stripe_utils import (
    create_ephemeral_key,
    create_payment_intent,
    initiate_payout_request,
    list_artist_transactions,
    list_transactions_for_a_customer,
    request_refund,
    retrieve_account_information,
    retrieve_connect_account_balance,
    update_account_information,
)

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

    # get details of the song which will be used to create the payment intent
    song_id = song.id  # id of the song
    song_price = song.price  # price of the song, this is a DecimalField.
    song_title = song.title  # title of the song
    artist = song.artist.username  # artist of the song

    artist_connect_id = ArtistCustomerProfile.objects.get(artist=song.artist).artistid
    customer_id = NormalCustomerProfile.objects.get(customer=request.user).customerid
    # create payment intent and ephemeral key
    # the ephemeral key will be used to save the customers payment method
    # on the stripe payment sheet on the client side.
    payment_intent = create_payment_intent(
        song_title, artist, song_id, song_price, artist_connect_id, customer_id
    )
    ephemeral_key = create_ephemeral_key(customer_id)
    data = {
        'client_secret': payment_intent.client_secret,
        'ephemeral_key': ephemeral_key,
    }
    return Response(
        return_structured_data('success', data, ''),
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def retrieve_account_balance(request):
    """
    Retrieve the account balance of an artist
    """
    artist_customer_profile = ArtistCustomerProfile.objects.get(artist=request.user)
    artist_id = artist_customer_profile.artistid
    try:
        balance_info: tuple = retrieve_connect_account_balance(artist_id)
    except stripe.error.InvalidRequestError:
        error_message = 'error retrieving account balance'
        return Response(return_structured_data('failure', '', error_message))
    # obtain the balance information from the balance_info tuple
    # balance_info[0] being the available balance, balance_info[1] being the
    # pending balance
    available_balance, pending_balance = balance_info
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
        response: dict = retrieve_account_information(artist_stripe_account_id)
    except stripe.error.InvalidRequestError:
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
    except ValueError:
        return Response(
            return_structured_data('failure', '', 'Could not parse stripe_data')
        )
    artistid = ArtistCustomerProfile.objects.get(artist=request.user).artistid
    try:
        response = update_account_information(artistid, stripe_data)
    except stripe.error.InvalidRequestError:
        return Response(
            return_structured_data('failure', '', 'Failed to update account info')
        )
    return Response(return_structured_data('success', response, ''))


@api_view(['GET'])
def display_thank_you(request):
    """
    Display the “Thank You” page
    """
    return Response(
        return_structured_data('success', '', 'Thank you for your purchase')
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, UserIsArtistOrError])
def request_payout(request):
    """
    Request a payout for an artist
    """
    artist = ArtistCustomerProfile.objects.get(artist=request.user)
    artist_stripe_account_id = artist.artistid
    # get account balance of user requesting the payout
    available_balance = retrieve_connect_account_balance(artist_stripe_account_id)[1]
    try:
        payment_request_response = initiate_payout_request(
            user_account=artist_stripe_account_id, amount=int(available_balance)
        )
    except stripe.error.InvalidRequestError as e:
        return Response(return_structured_data('failure', '', str(e.user_message)))
    return Response(return_structured_data('success', payment_request_response, ''))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, UserIsArtistOrError])
def retrieve_artist_transaction_history(request):
    """
    Retrieve the transaction history for an artist
    """
    artist_id = ArtistCustomerProfile.objects.get(artist=request.user).artistid
    response: dict = list_artist_transactions(artist_id)
    return Response(return_structured_data('success', response, ''))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def retrieve_customer_transaction_history(request):
    """
    Retrieve the transaction history for a customer
    """
    customer_id = NormalCustomerProfile.objects.get(customer=request.user).customerid
    response: dict = list_transactions_for_a_customer(customer_id)
    return Response(return_structured_data('success', response, ''))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def request_payment_refund(request, song_id: int):
    """
    Request a refund for a song
    """
    customer_id = NormalCustomerProfile.objects.get(customer=request.user).customerid
    try:
        response: dict = request_refund(customer_id, song_id)
    except stripe.error.InvalidRequestError:
        return Response(
            return_structured_data('failure', '', 'No successful charge to refund')
        )
    return Response(return_structured_data('success', response['status'], ''))
