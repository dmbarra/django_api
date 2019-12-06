from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.permissions.action_based_permission import ActionBasedPermission
from api.serializers.user_serializer import UserSerializer

HTTP_AUTHORIZATION = 'HTTP_AUTHORIZATION'


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsAuthenticated: ['update', 'partial_update', 'destroy', 'list', 'retrieve', ],
        AllowAny: ['create']
    }
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'put']

    def get_queryset(self):
        auth_token = self.request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        username = Token.objects.get(key=auth_token).user
        user = User.objects.get(username=username)

        if user.is_superuser:
            return User.objects.all().order_by('-date_joined')
        else:
            return User.objects.filter(username=user.username).order_by('-date_joined')

    def create(self, request):
        group = Group.objects.filter(name='candidates')
        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save(groups=group)
        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        user = User.objects.filter(author=user, pk=kwargs['pk'])
        if user:
            user_serializer = UserSerializer(data=request.data)
            user_serializer.is_valid(raise_exception=True)
            user.user_serializer(username=request.data['username'],
                                 email=request.data['email'],
                                 password=request.data['password'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
