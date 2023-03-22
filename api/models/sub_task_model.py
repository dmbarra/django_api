from django.db import models

from api.models.choices.status_choices import Status
from api.models.task_model import Task


class SubTask(models.Model):
    description = models.CharField(null=True, max_length=1000)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, null=True, choices=Status.choices, default=Status.NEW)
    due_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
