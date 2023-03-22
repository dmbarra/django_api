from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    body = models.CharField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
