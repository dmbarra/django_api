from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status

from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models.bug_model import Bug
from api.models.choices.status_choices import Status
from api.permissions.action_based_permission import ActionBasedPermission
from api.serializers.bug_serializer import BugSerializer

HTTP_AUTHORIZATION = 'HTTP_AUTHORIZATION'


class BugViewSet(viewsets.ModelViewSet):
    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsAuthenticated: ['update', 'partial_update', 'destroy', 'list', 'retrieve', 'create'],
    }
    queryset = Bug.objects.order_by('-created_at',)
    serializer_class = BugSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        auth_token = self.request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        return Bug.objects.filter(author=user, status__in=[Status.NEW, Status.UPDATED]).order_by('-created_at',)

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: BugSerializer,
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        },
        operation_id='Create new bug',
        operation_description='This endpoint to create new bug',
        request_body=BugSerializer,
    )
    def create(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        bug_serializer = BugSerializer(data=request.data)
        bug_serializer.is_valid(raise_exception=True)
        bug_serializer.save(author=user, status=Status.NEW)
        return Response(bug_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            status.HTTP_202_ACCEPTED: "Accepted",
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
        operation_id='Destroy a bug',
        operation_description='This endpoint to destroy a bug',
    )
    def destroy(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        bug = Bug.objects.filter(author=user, pk=kwargs['pk'])
        if bug:
            bug.update(status=Status.DELETED)
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: BugSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
        operation_id='Update a Bug',
        operation_description='This endpoint to update bug',
    )
    def partial_update(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        bug_set = Bug.objects.filter(author=user, pk=kwargs['pk'])
        if bug_set.first():
            bug_set.update(status=Status.UPDATED)
            bug_serializer = BugSerializer(bug_set.first(),
                                           data=request.data,
                                           partial=True)
            if bug_serializer.is_valid():
                bug_serializer.save()
            return Response(bug_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_id='List all bugs',
        operation_description='This endpoint to list all bugs',
    )
    def list(self, request, *args, **kwargs):
        return super(BugViewSet, self).list(request, args, kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: BugSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
        operation_id='Retrieve a bug',
        operation_description='This endpoint to retrieve bug',
    )
    def retrieve(self, request, *args, **kwargs):
        return super(BugViewSet, self).retrieve(request, args, kwargs)
