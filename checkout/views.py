import os

import stripe
from api.serializers import PaymentInfoSerializer
from api.utils import return_structured_data
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv

# from profiles.models import ArtistCustomerProfile
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from song.models import Song

load_dotenv()


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
        stripe.api_key = os.environ['STRIPE_SECRET_KEY']
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
