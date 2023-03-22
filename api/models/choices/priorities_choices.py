from django.db import models


class Priorities(models.TextChoices):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
