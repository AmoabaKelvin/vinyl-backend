import datetime
import json

from api.serializers import RegisterSerializer, UserSerializer
from api.utils import return_structured_data
from django.contrib.auth import login
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutView
from profiles.models import ArtistCustomerProfile, NormalCustomerProfile
from rest_framework import generics, permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response

from .utils import create_stripe_account


class SignUpView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            serializer_errors = ''  # Add serializer.errors to this string
            for key, value in serializer.errors.items():
                serializer_errors += f"{key}: {value[0]} "
            return Response(
                data=return_structured_data('failure', '', serializer_errors),
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.save()
        stripe_account_creation_data = json.loads(request.data['stripe_data'])
        # Pass the user object to the `stripe_account_creation_data` function
        # together with the stripe_data dictionary obtained from request.data,
        # the stripe_data will be used to create a stripe account for the artist
        create_stripe_account(user, stripe_account_creation_data)
        # get stripe_account_id and stripe_connect_id from the user object
        # but stripe_connect_id will be none if the user is not an artist
        stripe_connect_id = None
        if user.is_artist:
            stripe_connect_id = ArtistCustomerProfile.objects.get(artist=user).artistid
        stripe_account_id = NormalCustomerProfile.objects.get(customer=user).customerid
        token = AuthToken.objects.create(user=user)
        formatted_token_expiry_date = (
            AuthToken.objects.get(user=user).expiry,
            '%Y-%m-%d %H:%M:%S',
        )
        response_result = {
            'user': UserSerializer(user).data,
            'token': token[1],  # token[1] is the token
            'token_expiry': formatted_token_expiry_date,
            'stripe_account_id': stripe_account_id,
            'stripe_connect_id': stripe_connect_id,
        }
        return Response(
            data=return_structured_data('success', response_result, ''),
            status=status.HTTP_201_CREATED,
        )


class LoginView(KnoxLoginView):
    """
    Log a user using their tokens
    """

    permission_classes = (permissions.AllowAny,)

    def get_post_response_data(self, request, token, instance):
        # Override the default response data by adding the status and result
        # objects to the response data.
        data = super().get_post_response_data(request, token, instance)
        expiry_date = datetime.datetime.strptime(
            data['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ'
        )
        custom_json = {
            'status': 'success',
            'result': {
                'expiry': expiry_date,
                'token': data['token'],
            },
            'detail': '',
        }
        return custom_json

    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                return_structured_data(
                    'failure', '', 'Username or password is incorrect'
                )
            )
        user = serializer.validated_data['user']
        login(request, user)
        # call the super class to process the request and then override the
        # response data by adding the user, stripe_account_id and
        # stripe_connect_id to it.
        # The stripe_connect_id will be None if the user is not an artist.
        connect_id = None
        if user.is_artist:
            connect_id = ArtistCustomerProfile.objects.get(artist=user).artistid
        account_id = NormalCustomerProfile.objects.get(customer=user).customerid
        # Getting response data from the super class
        response = super(LoginView, self).post(request)
        response_data = response.data['result']
        response_data['user'] = UserSerializer(user).data
        response_data['stripe_account_id'] = account_id
        response_data['stripe_connect_id'] = connect_id
        return Response(response.data)


# Since the default LogoutView does not return any data to indicate that the user has been logged out,
# we need to override it to return the correct response.
class CustomLogoutView(LogoutView):
    def post(self, request, format=None):
        super(CustomLogoutView, self).post(request, format)
        return Response(return_structured_data('success', '', ''))
