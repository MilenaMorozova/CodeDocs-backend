from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from.models import CustomUser


class UserSerializer(serializers.ModelSerializer):

    account_color = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()

    class Meta(object):
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'account_color', 'is_active')
        extra_kwargs = {'password': {'write_only': True}}


class UserRegistrationSerializer(UserCreateSerializer):
    account_color = serializers.ReadOnlyField()

    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'username', 'email', 'password', 'account_color')

# TODO create necessary serializers, token settings, customize messanges in email, tests, function get_short_name
