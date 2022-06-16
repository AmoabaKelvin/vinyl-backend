import os

import stripe
from api.utils import return_structured_data
from profiles.models import ArtistCustomerProfile, NormalCustomerProfile
from rest_framework.response import Response


def create_stripe_account(instance, stripe_data: dict):
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    try:
        customer = stripe.Customer.create(
            email=instance.email,
            description=instance.username,
        )
        NormalCustomerProfile.objects.create(customer=instance, customerid=customer.id)
        if instance.is_artist:
            # create a stripe account for the artist
            # this account will be used for receiving payments in the future
            # Pass the stripe_data to the individual argument.
            artist_account = stripe.Account.create(
                type="express",
                country="US",
                email=instance.email,
                business_type="individual",
                individual=stripe_data,
            )
            ArtistCustomerProfile.objects.create(
                artist=instance, artistid=artist_account.id
            )
    except stripe.error as e:
        # If there is any error encounted during the account creation process,
        # return a Response to the client with the error message
        return Response(
            data=return_structured_data('failure', '', e.user_message),
        )
