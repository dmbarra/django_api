import django_filters

from api.models.bug_model import Bug


class BugFilter(django_filters.FilterSet):
    class Meta:
        model = Bug
        fields = ['author', 'title', 'priority', 'status']
