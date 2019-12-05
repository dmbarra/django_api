from django.contrib.auth.models import Group, User
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from api.serializers.group_serializer import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_queryset(self):
        auth_token = self.request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
        username = Token.objects.get(key=auth_token).user
        user = User.objects.get(username=username)

        if user.is_superuser:
            return Group.objects.all()
        else:
            return Group.objects.filter(name='invalid')

    def create(self, request):
        auth_token = request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user

        if user.is_superuser:
            return super(GroupViewSet, self).create(request)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

