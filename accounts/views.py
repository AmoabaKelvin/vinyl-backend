import datetime

from api.serializers import RegisterSerializer, UserSerializer
from django.contrib.auth import login
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutView
from profiles.models import ArtistCustomerProfile, NormalCustomerProfile
from rest_framework import generics, permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response


class SignUpView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            serializer_errors = ''
            for key, value in serializer.errors.items():
                # add error to serializer_errors variable
                serializer_errors += f"{key}: {value[0]} "
            return Response(
                data={
                    'status': 'failure',
                    'result': '',
                    'details': serializer_errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.save()
        return Response(
            {
                'status': 'success',
                'result': {
                    'user': UserSerializer(user, context=self.get_serializer_context()).data,
                    'token': AuthToken.objects.create(user)[1],
                    'is_artist': user.is_artist,
                    'customer_id': NormalCustomerProfile.objects.get(customer=user).customerid,
                    'artist_id': ArtistCustomerProfile.objects.get(artist=user).artistid if user.is_artist else None,
                },
                'details': '',
            }
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
        expiry_date = datetime.datetime.strptime(data['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ')
        custom_json = {
            'status': 'success',
            'result': {
                'expiry': expiry_date.strftime("%m/%d/%Y, %H:%M:%S"),
                'token': data['token'],
            },
        }
        return custom_json

    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        response = super(LoginView, self).post(request)
        response.data['result']['user'] = UserSerializer(user).data
        response.data['result']['customer_id'] = NormalCustomerProfile.objects.get(customer=user).customerid
        response.data['result']['artist_id'] = (
            ArtistCustomerProfile.objects.get(artist=user).artistid if user.is_artist else None
        )
        return Response(response.data)


# Since the default LogoutView does not return any data to indicate that the user has been logged out,
# we need to override it to return the correct response.
class CustomLogoutView(LogoutView):
    def post(self, request, format=None):
        super(CustomLogoutView, self).post(request, format)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
