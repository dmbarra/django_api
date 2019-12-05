from rest_framework import serializers

from api.models.bug_model import Bug


class BugSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bug
        fields = ['title', 'description', 'priority']
