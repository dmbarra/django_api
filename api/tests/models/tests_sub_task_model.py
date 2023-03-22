from django.contrib.auth.models import User
from django.test import TestCase

from api.models.sub_task_model import SubTask
from api.models.task_model import Task


class SubTaskModelTest(TestCase):

    def test_sub_task_fields(self):
        user = self.create_user()
        task = self.create_task(user)
        sub_task = self.create_sub_task(task)
        self.assertTrue(isinstance(sub_task, SubTask))
        self.assertEqual(sub_task.task, task)
        self.assertEqual(sub_task.description, 'Sub task body message')
        self.assertEqual(sub_task.status, 'NEW')

    @staticmethod
    def create_sub_task(task):
        return SubTask.objects.create(description='Sub task body message', status='NEW', task=task)

    @staticmethod
    def create_task(user):
        return Task.objects.create(body='Task body message', status='NEW', author=user)

    @staticmethod
    def create_user():
        return User.objects.create(username='username', password='password', email='email')
