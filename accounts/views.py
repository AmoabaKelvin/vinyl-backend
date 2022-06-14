from api.serializers import RegisterSerializer, UserSerializer
from django.contrib.auth import login
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutView
from rest_framework import generics, permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response


class SignUpView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


class LoginView(KnoxLoginView):
    """
    Log a user using their tokens
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request)


# Since the default LogoutView does not return any data to indicate that the user has been logged out,
# we need to override it to return the correct response.
class CustomLogoutView(LogoutView):
    def post(self, request, format=None):
        super(CustomLogoutView, self).post(request, format)
        return Response({"logged_out": True}, status=status.HTTP_200_OK)
