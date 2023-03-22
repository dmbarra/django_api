from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models.choices.status_choices import Status
from api.models.sub_task_model import SubTask
from api.models.task_model import Task
from api.permissions.action_based_permission import ActionBasedPermission
from api.serializers.sub_task_serializer import SubTaskSerializer

HTTP_AUTHORIZATION = 'HTTP_AUTHORIZATION'


class SubTaskViewSet(viewsets.ModelViewSet):
    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsAuthenticated: ['update', 'partial_update', 'destroy', 'list', 'retrieve', 'create'],
    }
    queryset = SubTask.objects.order_by('-created_at',)
    serializer_class = SubTaskSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        auth_token = self.request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        task = get_object_or_404(Task, author=user,  pk=self.kwargs['task_pk'], status__in=['NEW', 'UPDATED'])
        return SubTask.objects.filter(task=task, status__in=[Status.NEW, Status.UPDATED]).order_by('-created_at',)

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: SubTaskSerializer,
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        },
        operation_id='Create new SubTask',
        operation_description='This endpoint to create new SubTask',
        request_body=SubTaskSerializer,
    )
    def create(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        task = get_object_or_404(Task, author=user, pk=self.kwargs['task_pk'], status__in=['NEW', 'UPDATED'])
        sub_task_serializer = SubTaskSerializer(data=request.data)
        sub_task_serializer.is_valid(raise_exception=True)
        sub_task_serializer.save(task=task, status='NEW')
        return Response(sub_task_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={
            status.HTTP_202_ACCEPTED: "Accepted",
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
        operation_id='Destroy a SubTask',
        operation_description='This endpoint to destroy a SubTask',
    )
    def destroy(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        task = get_object_or_404(Task, author=user, pk=self.kwargs['task_pk'], status__in=['NEW', 'UPDATED'])
        sub_task = SubTask.objects.filter(task=task, pk=kwargs['pk'])
        if sub_task:
            sub_task.update(status=Status.DELETED)
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: SubTaskSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
        operation_id='Update a SubTask',
        operation_description='This endpoint to update SubTask',
    )
    def partial_update(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        task = get_object_or_404(Task, author=user, pk=self.kwargs['task_pk'], status__in=['NEW', 'UPDATED'])
        sub_task_set = SubTask.objects.filter(task=task, pk=kwargs['pk'])
        if sub_task_set.first():
            sub_task_set.update(status=Status.UPDATED)
            sub_task_serializer = SubTaskSerializer(sub_task_set.first(),
                                                    data=request.data,
                                                    partial=True)
            if sub_task_serializer.is_valid():
                sub_task_serializer.save()
            return Response(sub_task_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_id='List all SubTasks',
        operation_description='This endpoint to list all SubTasks',
    )
    def list(self, request, *args, **kwargs):
        return super(SubTaskViewSet, self).list(request, args, kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: SubTaskSerializer,
            status.HTTP_404_NOT_FOUND: "Not Found",
        },
        operation_id='Retrieve a SubTask',
        operation_description='This endpoint to retrieve SubTask',
    )
    def retrieve(self, request, *args, **kwargs):
        return super(SubTaskViewSet, self).retrieve(request, args, kwargs)
