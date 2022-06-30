from accounts.models import CustomUser
from django.db import models


class ArtistCustomerProfile(models.Model):
    artist = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='artist_profile'
    )
    artistid = models.CharField(max_length=100)


class NormalCustomerProfile(models.Model):
    customer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='normal_profile'
    )
    customerid = models.CharField(max_length=100)
