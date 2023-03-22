from django.contrib.auth.models import User
from django.test import TestCase

from api.models.task_model import Task


class TaskModelTest(TestCase):

    def test_task_fields(self):
        user = self.create_user()
        task = self.create_task(user)
        self.assertTrue(isinstance(task, Task))
        self.assertEqual(task.author, user)
        self.assertEqual(task.body, 'Task body message')
        self.assertEqual(task.status, 'NEW')

    @staticmethod
    def create_task(user):
        return Task.objects.create(body='Task body message', status='NEW', author=user)

    @staticmethod
    def create_user():
        return User.objects.create(username='username', password='password', email='email')
