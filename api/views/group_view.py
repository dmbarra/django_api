from django.contrib.auth.models import Group, User
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions.action_based_permission import ActionBasedPermission
from api.serializers.group_serializer import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsAuthenticated: ['update', 'partial_update', 'destroy', 'list', 'retrieve', 'create'],
    }
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        auth_token = self.request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
        username = Token.objects.get(key=auth_token).user
        user = User.objects.get(username=username)

        if user.is_superuser:
            return Group.objects.all()
        else:
            return Group.objects.filter(name='invalid')

    def create(self, request, *args, **kwargs):
        auth_token = request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user

        if user.is_superuser:
            group_serializer = GroupSerializer(data=request.data)
            group_serializer.is_valid(raise_exception=True)
            group = group_serializer.save()
            return Response({'id': group.pk}, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

