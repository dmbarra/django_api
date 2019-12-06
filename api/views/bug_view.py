from rest_framework import viewsets, status

from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models.bug_model import Bug
from api.permissions.action_based_permission import ActionBasedPermission
from api.serializers.bug_serializer import BugSerializer


class BugViewSet(viewsets.ModelViewSet):
    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsAuthenticated: ['update', 'partial_update', 'destroy', 'list', 'retrieve', 'create'],
    }
    queryset = Bug.objects.order_by('-created_at',)
    serializer_class = BugSerializer

    def get_queryset(self):
        auth_token = self.request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        return Bug.objects.filter(author=user).order_by('-created_at',)

    def create(self, request):
        auth_token = request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
        user = Token.objects.get(key=auth_token).user
        bug_serializer = BugSerializer(data=request.data)
        bug_serializer.is_valid(raise_exception=True)
        bug_serializer.save(author=user)
        return Response(status=status.HTTP_201_CREATED)
