from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals


class LoginInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField()


def user_pre_save(sender, instance, **kwargs):
    if instance.last_login:
        old = instance.__class__.objects.get(pk=instance.pk)
        if instance.last_login != old.last_login:
            instance.logininfo_set.create(timestamp=instance.last_login)


signals.pre_save.connect(user_pre_save, sender=User)
