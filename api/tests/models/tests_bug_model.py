from django.contrib.auth.models import User
from django.test import TestCase

from api.models.bug_model import Bug


class BugModelTest(TestCase):

    def test_bug_fields(self):
        user = self.create_user()
        bug = self.create_bug(user)
        self.assertTrue(isinstance(bug, Bug))
        self.assertEqual(bug.author, user)
        self.assertEqual(bug.title, 'Bug')
        self.assertEqual(bug.description, 'description')
        self.assertEqual(bug.priority, 'HIGH')
        self.assertEqual(bug.status, 'NEW')

    @staticmethod
    def create_bug(user):
        return Bug.objects.create(title='Bug', description='description', priority='HIGH', status='NEW', author=user)

    @staticmethod
    def create_user():
        return User.objects.create(username='username', password='password', email='email')
