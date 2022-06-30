import os

import stripe
from api.utils import return_structured_data
from django.db.models.signals import post_save
from django.dispatch import receiver
from profiles.models import ArtistCustomerProfile, NormalCustomerProfile
from rest_framework.response import Response

from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def create_stripe_account(instance, created, **kwargs):
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    if created:
        try:
            customer = stripe.Customer.create(
                email=instance.email,
                description=instance.username,
            )
            NormalCustomerProfile.objects.create(
                customer=instance, customerid=customer.id
            )
            if instance.is_artist:
                # create a stripe account for the artist
                # this account will be used for receiving payments in the future
                # Pass the stripe_data to the individual argument.
                artist_account = stripe.Account.create(
                    type="express",
                    country="US",
                    email=instance.email,
                    capabilities={
                        "card_payments": {"requested": True},
                        "transfers": {"requested": True},
                    },
                )
                ArtistCustomerProfile.objects.create(
                    artist=instance,
                    artistid=artist_account.id,
                )
        except stripe.error.InvalidRequestError as e:
            # If there is any error encounted during the account creation process,
            # return a Response to the client with the error message
            return Response(
                data=return_structured_data('failure', '', e.user_message),
            )
