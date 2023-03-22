from django.contrib.auth.models import User
from django.db import models

from api.models.choices.priorities_choices import Priorities
from api.models.choices.status_choices import Status


class Bug(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    priority = models.CharField(max_length=50, choices=Priorities.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
