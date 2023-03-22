from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token

from api.models.bug_model import Bug
from api.models.sub_task_model import SubTask
from api.models.task_model import Task


class FactoryData:

    @staticmethod
    def create_bug(user, status='NEW'):
        return Bug.objects.create(title='Bug', description='description', priority='HIGH', status=status, author=user)

    @staticmethod
    def create_token(user):
        return Token.objects.create(user=user)

    @staticmethod
    def create_group(group='default'):
        return Group.objects.create(name=group)

    @staticmethod
    def create_task(user, status='NEW'):
        return Task.objects.create(body='Task body message', status=status, author=user)

    @staticmethod
    def create_sub_task(task, status='NEW'):
        return SubTask.objects.create(description='Sub task body message', status=status, task=task, due_date='2019-09-22T00:00:00')

    @staticmethod
    def create_user(user='username', root=False):
        return User.objects.create(username=user, password='password', email='email', first_name='name', is_superuser=root)

    @staticmethod
    def create_user_and_save(user='username', root=False):
        user = User.objects.create(username=user, password='password', email='email', first_name='name', is_superuser=root)
        user.set_password('password')
        user.save()

