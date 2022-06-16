import os

import stripe
from django.db.models.signals import post_save
from django.dispatch import receiver
from dotenv import load_dotenv
from profiles.models import ArtistCustomerProfile, NormalCustomerProfile

from accounts.models import CustomUser

load_dotenv()

# Whenever a new user signs up, create a stripe customer account for them
@receiver(post_save, sender=CustomUser)
def create_stripe_customer(sender, instance, created, **kwargs):
    if created:
        # Create a stripe customer account for the user
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        customer = stripe.Customer.create(
            email=instance.email,
            description=instance.username,
        )
        NormalCustomerProfile.objects.create(customer=instance, customerid=customer.id)
        if instance.is_artist:
            # create a stripe account for the artist
            # this account will be used for receiving payments in the future
            artist_account = stripe.Account.create(
                type="express",
                country="US",
                email=instance.email,
            )
            # create a customer profile for the artist
            ArtistCustomerProfile.objects.create(artist=instance, artistid=artist_account.id)
