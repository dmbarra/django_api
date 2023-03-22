from django.contrib.auth.models import User, Group
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, filters
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
    search_fields = ['username', 'email']
    filter_backends = (filters.SearchFilter,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        auth_token = self.request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        username = Token.objects.get(key=auth_token).user
        user = User.objects.get(username=username)

        if user.is_superuser:
            return User.objects.all().order_by('-date_joined')
        else:
            return User.objects.filter(username=user.username).order_by('-date_joined')

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: UserSerializer,
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        },
        security=[],
        operation_id='Create new user',
        operation_description='This endpoint to create new user',
        request_body=UserSerializer,
    )
    def create(self, request, *args, **kwargs):
        serializer_context = {
            'request': request,
        }
        group, created = Group.objects.get_or_create(name='candidates')
        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user = User.objects.create(username=request.data['username'],
                                   email=request.data['email'],
                                   first_name=request.data['name']
                                   )
        user.set_password(request.data['password'])
        group.user_set.add(user)
        user.save()
        return Response(UserSerializer(user, context=serializer_context,).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
        operation_id='Update a user',
        operation_description='This endpoint to update user',
    )
    def partial_update(self, request, *args, **kwargs):
        serializer_context = {
            'request': request,
        }

        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user_name = Token.objects.get(key=auth_token).user
        user = User.objects.filter(username=user_name, pk=kwargs['pk']).first()
        if user:
            user_serializer = UserSerializer(user,
                                             data=request.data,
                                             context=serializer_context,
                                             partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_id='List all users',
        operation_description='This endpoint to list all users',
    )
    def list(self, request, *args, **kwargs):
        return super(UserViewSet, self).list(request, args, kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
        operation_id='Retrieve a user',
        operation_description='This endpoint to retrieve user',
    )
    def retrieve(self, request, *args, **kwargs):
        return super(UserViewSet, self).retrieve(request, args, kwargs)
