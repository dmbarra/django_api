from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from rest_framework import filters, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.permissions.action_based_permission import ActionBasedPermission
from api.serializers.profile_serializer import ProfileSerializer

HTTP_AUTHORIZATION = 'HTTP_AUTHORIZATION'


class ProfileViewSet(viewsets.ModelViewSet):
    swagger_schema = None
    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsAuthenticated: ['update', 'partial_update', 'destroy', 'list', 'retrieve', ],
        AllowAny: ['create']
    }
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    http_method_names = ['get']

    def get_queryset(self):
        auth_token = self.request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        username = Token.objects.get(key=auth_token).user
        user = User.objects.get(username=username)
        if user.is_superuser:
            return User.objects.filter(id=self.kwargs.get('user_pk'))
        else:
            raise PermissionDenied
