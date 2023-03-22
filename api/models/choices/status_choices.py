from django.db import models


class Status(models.TextChoices):
    NEW = "NEW"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
