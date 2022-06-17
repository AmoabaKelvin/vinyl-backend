import os

import stripe
from api.serializers import PaymentInfoSerializer
from api.utils import return_structured_data
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from profiles.models import ArtistCustomerProfile

# from profiles.models import ArtistCustomerProfile
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from song.models import Song

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def buy_song(request, song_id):
    """
    Process the payment for a song
    """
    # Use the song_id to get the song object and then retrieve the price of
    # the song.
    song = get_object_or_404(Song, id=song_id)
    # get payment data from serializer
    payment_serializer_data = PaymentInfoSerializer(data=request.data)
    if payment_serializer_data.is_valid():
        amount = payment_serializer_data.validated_data['amount']
        currency = payment_serializer_data.validated_data['currency']
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount),
            currency=currency,
            description=f"Payment for song {song.title}-{song.artist}",
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
    available_balance = response['available'][0]['amount']
    pending_balance = response['pending'][0]['amount']
    response_data = {
        'available_balance': available_balance,
        'pending_balance': pending_balance,
    }
    return Response(return_structured_data('success', response_data, ''))
