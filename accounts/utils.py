import os

import stripe
from profiles.models import ArtistCustomerProfile, NormalCustomerProfile


def create_stripe_customer(instance, stripe_data: dict):
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    customer = stripe.Customer.create(
        email=instance.email,
        description=instance.username,
    )
    NormalCustomerProfile.objects.create(customer=instance, customerid=customer.id)
    if instance.is_artist:
        # create a stripe account for the artist
        # this account will be used for receiving payments in the future
        try:
            artist_account = stripe.Account.create(
                type="express",
                country="US",
                email=instance.email,
                business_type="individual",
                individual=stripe_data,
            )
            ArtistCustomerProfile.objects.create(artist=instance, artistid=artist_account.id)
        except stripe.error.InvalidRequestError as e:
            pass
