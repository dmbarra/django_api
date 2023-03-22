from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, status
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response

from api.authentication.token_expire_handler import token_expire_handler, expires_in
from api.serializers.error_serializer import ErrorResponseSerializer
from api.serializers.token_serializer import TokenSerializer, TokenResponseSerializer


class TokenViewSet(viewsets.ModelViewSet):

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenResponseSerializer,
            status.HTTP_400_BAD_REQUEST: ErrorResponseSerializer(),
            status.HTTP_404_NOT_FOUND: ErrorResponseSerializer()
        },
        security=[],
        operation_id='Generate Token',
        operation_description='This endpoint to create token for be used in all requests',
        methods=['post'],
        request_body=TokenSerializer,
    )
    @csrf_exempt
    @api_view(["POST"])
    @permission_classes((AllowAny,))
    def login(request):
        username = request.data.get("username")
        password = request.data.get("password")

        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'}, status=HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if not user:
            return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)

        token, _ = Token.objects.get_or_create(user=user)
        is_expired, token = token_expire_handler(token)

        update_last_login(None, user)

        return Response({'token': token.key,
                         'userId': user.id,
                         'seconds_to_expire': expires_in(token).seconds, }, status=HTTP_200_OK)

