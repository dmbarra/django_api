from django.contrib.auth.models import Group
from rest_framework import viewsets
from api.serializers.group_serializer import GroupSerializer
from rest_framework.permissions import IsAuthenticated


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
