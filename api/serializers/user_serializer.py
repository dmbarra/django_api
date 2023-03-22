from django.contrib.auth.models import User
from django.core.validators import validate_email
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='first_name',
                                 required=True,
                                 error_messages={"blank": "Name cannot be empty."})
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     error_messages={"blank": "Password cannot be empty."})
    email = serializers.CharField(required=True,
                                  validators=[validate_email],
                                  error_messages={"blank": "Email cannot be empty."})
    username = serializers.CharField(required=True,
                                     error_messages={"blank": "Username cannot be empty."})

    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email', 'name', 'password']
        read_only_fields = ['id', 'email', 'username']

