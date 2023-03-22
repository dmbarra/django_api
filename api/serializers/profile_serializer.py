from django.db.models import Count
from rest_framework import serializers

from api.serializers.user_serializer import UserSerializer


class ProfileSerializer(UserSerializer):
    total_bugs = serializers.SerializerMethodField(read_only=True)
    active_bugs = serializers.SerializerMethodField(read_only=True)
    total_tasks = serializers.SerializerMethodField(read_only=True)
    last_login = serializers.SerializerMethodField(read_only=True)
    date_joined = serializers.SerializerMethodField(read_only=True)
    total_logins = serializers.SerializerMethodField(read_only=True)
    total_subtasks = serializers.SerializerMethodField(read_only=True)

    def get_total_bugs(self, user):
        return user.bug_set.count()

    def get_active_bugs(self, user):
        return user.bug_set.exclude(status="DELETED").count()

    def get_total_tasks(self, user):
        return user.task_set.count()

    def get_last_login(self, user):
        return user.last_login

    def get_date_joined(self, user):
        return user.date_joined.__str__()

    def get_total_logins(self, user):
        return user.logininfo_set.count()

    def get_total_subtasks(self, user):
        return user.task_set.all().aggregate(total_subtasks=Count('subtask'))['total_subtasks']

    class Meta(UserSerializer.Meta):
        profile_fields = ['active_bugs', 'total_bugs', 'total_tasks', 'last_login', 'date_joined', 'total_logins', 'total_subtasks']
        fields = UserSerializer.Meta.fields + profile_fields
