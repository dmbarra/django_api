from rest_framework import serializers

from api.models.sub_task_model import SubTask


class SubTaskSerializer(serializers.HyperlinkedModelSerializer):
    description = serializers.CharField(allow_blank=False, required=True, max_length=250)
    due_date = serializers.DateTimeField(required=True)

    class Meta:
        model = SubTask
        fields = ['id', 'description', 'status', 'due_date']
        read_only_fields = ['id', 'status']
