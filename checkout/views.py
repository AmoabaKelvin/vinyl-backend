import os

import stripe
from api.serializers import PaymentInfoSerializer
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from profiles.models import ArtistCustomerProfile
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from song.models import Song

from .utils import calculate_application_fee

load_dotenv()


@api_view(['POST'])
def buy_song(request, song_id):
    """
    Process the payment for a song
    """
    # Use the song_id to get the song object and then retrieve the price of
    # the song.
    song = get_object_or_404(Song, id=song_id)
    # Get the credit card information from the request body.
    payment_serializer_data = PaymentInfoSerializer(data=request.data)
    if payment_serializer_data.is_valid():
        stripe.api_key = os.environ['STRIPE_SECRET_KEY']
        # The request data is a dictionary of the data needed to create
        # the payment intent.
        amount = payment_serializer_data.validated_data['amount']
        currency = payment_serializer_data.validated_data['currency']
        # get the artists customer id from the artist profile
        # artist_customer_id = ArtistCustomerProfile.objects.get(artist=song.artist).customer_id
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount),
            currency=currency,
            description=f"Payment for song {song.title}-{song.artist}",
            # application_fee_amount=calculate_application_fee(amount),
            # transfer_data={
            #     # get the connected account id of the artist
            #     'destination': str(artist_customer_id),
            # },
        )
        return Response(
            data={
                'status': 'success',
                'result': payment_intent.client_secret,
                'details': '',
            },
            status=status.HTTP_200_OK,
        )
