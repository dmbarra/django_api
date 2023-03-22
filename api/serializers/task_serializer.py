from rest_framework import serializers

from api.models.task_model import Task


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    body = serializers.CharField(min_length=3, max_length=250)
    total_subtasks = serializers.SerializerMethodField()

    def get_total_subtasks(self, task):
        return task.subtask_set.count()

    class Meta:
        model = Task
        fields = ['id', 'body', 'status', 'total_subtasks']
        read_only_fields = ['id', 'total_subtasks', 'status']
