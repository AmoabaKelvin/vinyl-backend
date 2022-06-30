from rest_framework import permissions


class UserIsArtistOrReadOnly(permissions.BasePermission):
    """
    Check whether the user of the incoming request has is_artist set to true
    before allowing for a `POST` request.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            # An authorization header should always be present in a POST request.
            # That will be used to determine the user.
            return request.user.is_artist
        return True


class UserIsArtistOrError(permissions.BasePermission):
    """
    Check whether the user of the incoming request has is_artist set to true
    before allowing for a `GET` request.
    """

    def has_permission(self, request, view):
        return bool(request.user.is_artist)
