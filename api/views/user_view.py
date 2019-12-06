from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.permissions.action_based_permission import ActionBasedPermission
from api.serializers.user_serializer import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsAuthenticated: ['update', 'partial_update', 'destroy', 'list', 'retrieve', ],
        AllowAny: ['create']
    }
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        auth_token = self.request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
        username = Token.objects.get(key=auth_token).user
        user = User.objects.get(username=username)

        if user.is_superuser:
            return User.objects.all().order_by('-date_joined')
        else:
            return User.objects.filter(username=user.username).order_by('-date_joined')
