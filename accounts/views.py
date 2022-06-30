import datetime

import stripe
from api.serializers import RegisterSerializer, UserSerializer
from api.utils import return_structured_data
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutView
from profiles.models import ArtistCustomerProfile, NormalCustomerProfile
from rest_framework import generics, permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


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
        stripe_connect_id = None
        onboarding = None

        if user.is_artist:
            stripe_connect_id = ArtistCustomerProfile.objects.get(artist=user).artistid
            onboarding = stripe.AccountLink.create(
                account=stripe_connect_id,
                refresh_url="https://project-vinyl-backend.herokuapp.com/api/checkout/done",
                return_url="https://project-vinyl-backend.herokuapp.com/api/checkout/done",
                type="account_onboarding",
            ).url
        stripe_account_id = NormalCustomerProfile.objects.get(customer=user).customerid
        token = AuthToken.objects.create(user=user)
        formatted_token_expiry_date = datetime.datetime.strftime(
            AuthToken.objects.get(user=user).expiry, '%Y-%m-%d %H:%M:%S'
        )
        response_result = {
            'user': UserSerializer(user).data,
            'token': token[1],  # token[1] is the token
            'token_expiry': formatted_token_expiry_date,
            'stripe_account_id': stripe_account_id,
            'stripe_connect_id': stripe_connect_id,
            # 'ephemeral_key': ephemeral_key,
            'onboarding_url': onboarding,
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
            try:
                connect_id = ArtistCustomerProfile.objects.get(artist=user).artistid
            except ArtistCustomerProfile.DoesNotExist:
                return Response(
                    return_structured_data('failure', '', 'Artist not found')
                )
        customer = get_object_or_404(NormalCustomerProfile, customer=user)
        account_id = customer.customerid
        # Getting response data from the super class
        response = super(LoginView, self).post(request)
        response_data = response.data['result']
        response_data['user'] = UserSerializer(user).data
        response_data['stripe_account_id'] = account_id
        response_data['stripe_connect_id'] = connect_id
        # response_data['ephemeral_key'] = customer.ephemeral_key
        return Response(response.data)


# Since the default LogoutView does not return any data to indicate that the user
# has been logged out,we need to override it to return the correct response.
class CustomLogoutViews(LogoutView):
    def post(self, request, format=None):
        super(CustomLogoutView, self).post(request, format)
        return Response(return_structured_data('success', '', ''))


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def delete_user_account(request):
    """
    Delete the user's account.
    """
    user = request.user
    # get the user's stripe account id and customer id and then delete them as
    # well.
    if user.is_artist:
        stripe_connect_id = ArtistCustomerProfile.objects.get(artist=user).artistid
        stripe.Account.delete(stripe_connect_id)
    customer_id = NormalCustomerProfile.objects.get(customer=user).customerid
    stripe.Customer.delete(customer_id)
    user.delete()
    return Response(return_structured_data('success', '', ''))
