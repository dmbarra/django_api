from rest_framework import viewsets, status

from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models.bug_model import Bug
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
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        auth_token = self.request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        return Bug.objects.filter(author=user, status__in=['NEW', 'UPDATED']).order_by('-created_at',)

    def create(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        bug_serializer = BugSerializer(data=request.data)
        bug_serializer.is_valid(raise_exception=True)
        bug_serializer.save(author=user, status='NEW')
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        bug = Bug.objects.filter(author=user, pk=kwargs['pk'])
        if bug:
            bug.update(status='DEACTIVATE')
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        auth_token = request.META.get(HTTP_AUTHORIZATION, '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        bug = Bug.objects.filter(author=user, pk=kwargs['pk'])
        if bug:
            bug_serializer = BugSerializer(data=request.data)
            bug_serializer.is_valid(raise_exception=True)
            bug.update(title=request.data['title'],
                       description=request.data['description'],
                       priority=request.data['priority'],
                       status='UPDATED')
            return Response(bug_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
