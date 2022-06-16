from django.contrib import admin

from .models import ArtistCustomerProfile, NormalCustomerProfile

admin.site.register([ArtistCustomerProfile, NormalCustomerProfile])
