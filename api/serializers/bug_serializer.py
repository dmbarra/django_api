from rest_framework import serializers
from api.models.bug_model import Bug


class BugSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bug
        fields = ['id', 'title', 'description', 'priority']
        read_only_fields = ['id']

