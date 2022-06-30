from accounts.models import CustomUser
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from song.models import Song


class SongSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    artist = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Song
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'is_artist', 'songs')


# serializers pertaining to authentication
class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    """

    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    first_name = serializers.CharField(required=True, min_length=3)
    last_name = serializers.CharField(required=True, min_length=3)
    # set password and password2 write_only to True to ensure they are only
    # used for creating and updating but not to be included when serializing data.
    password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password2',
            'is_artist',
        )

    def validate(self, attrs):
        """
        Check whether the two entered passwords match
        """
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError(
                {
                    'password': 'Passwords do not match. Ensure that you have entered the same password twice.'
                }
            )
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user
        """
        user = CustomUser.objects.create(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            is_artist=validated_data.get('is_artist'),
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize instances of the `CustomUser` model.
    """

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'is_artist', 'password')
        # setting the password to write_only ensures that it is not included
        # in the serialized data
        extra_kwargs = {'password': {'write_only': True}}


class PaymentInfoSerializer(serializers.Serializer):
    """
    Serializer for the payment info model.
    """

    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3)
