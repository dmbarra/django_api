from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models.choices.status_choices import Status
from api.models.task_model import Task
from api.permissions.action_based_permission import ActionBasedPermission
from api.serializers.task_serializer import TaskSerializer

HTTP_AUTHORIZATION = 'HTTP_AUTHORIZATION'


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsAuthenticated: ['update', 'partial_update', 'destroy', 'list', 'retrieve', 'create'],
    }
    queryset = Task.objects.order_by('-created_at',)
    serializer_class = TaskSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        auth_token = self.request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        return Task.objects.filter(author=user, status__in=[Status.NEW, Status.UPDATED]).order_by('-created_at',)

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: TaskSerializer,
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        },
        operation_id='Create new Task',
        operation_description='This endpoint to create new Task',
        request_body=TaskSerializer,
    )
    def create(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        task_serializer = TaskSerializer(data=request.data)
        task_serializer.is_valid(raise_exception=True)
        task_serializer.save(author=user, status='NEW')
        return Response(task_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            status.HTTP_202_ACCEPTED: "Accepted",
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
        operation_id='Destroy a Task',
        operation_description='This endpoint to destroy a Task',
    )
    def destroy(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        task = Task.objects.filter(author=user, pk=kwargs['pk'])
        if task:
            task.update(status=Status.DELETED)
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TaskSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
        operation_id='Update a Task',
        operation_description='This endpoint to update Task',
    )
    def partial_update(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        task_set = Task.objects.filter(author=user, pk=kwargs['pk'])
        if task_set.first():
            task_set.update(status=Status.UPDATED)
            task_serializer = TaskSerializer(task_set.first(),
                                             data=request.data,
                                             partial=True)
            if task_serializer.is_valid():
                task_serializer.save()
            return Response(task_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_id='List all Tasks',
        operation_description='This endpoint to list all Tasks',
    )
    def list(self, request, *args, **kwargs):
        return super(TaskViewSet, self).list(request, args, kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TaskSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
        operation_id='Retrieve a Task',
        operation_description='This endpoint to retrieve Task',
    )
    def retrieve(self, request, *args, **kwargs):
        return super(TaskViewSet, self).retrieve(request, args, kwargs)
