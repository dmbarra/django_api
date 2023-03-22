import django_filters
from django.contrib.auth.models import Group


class GroupFilter(django_filters.FilterSet):
    class Meta:
        model = Group
        fields = ['url', 'name', ]
