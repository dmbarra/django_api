from rest_framework import serializers


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        fields = ['username', 'password']


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    userId = serializers.IntegerField()
    seconds_to_expire = serializers.IntegerField()

    class Meta:
        fields = ['token', 'userId', 'seconds_to_expire']
