from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate
from rest_framework.utils import json
from django.core import serializers

from api.models.bug_model import Bug
from api.views.bug_view import BugViewSet


class BugViewTest(TestCase):

    def test_get_bug_without_token(self):
        user = self.create_user(False)
        self.create_bug(user)
        request = RequestFactory().get('v1/api/bugs')
        request.user = AnonymousUser()
        resp = BugViewSet.as_view({'get': 'list'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_get_bug_with_token(self):
        user = self.create_user(False)
        bug = self.create_bug(user)
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().get('v1/api/bugs', HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'get': 'list'})(request)

        bug_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug_response['count'], 1)
        self.assertEqual(bug_response['results'][0]['title'], bug.title)

    def test_get_bug_with_token_from_another_user(self):
        user = self.create_user(False)
        user2 = self.create_user('user2', False)
        self.create_bug(user)
        token = self.create_token(user2)
        token.generate_key()
        request = RequestFactory().get('v1/api/bugs', HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'get': 'list'})(request)

        bug_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug_response['count'], 0)

    def test_retrieve_bug_with_token_from_another_user(self):
        user = self.create_user(False)
        user2 = self.create_user('user2', False)
        new_bug = self.create_bug(user)
        token = self.create_token(user2)
        token.generate_key()
        request = RequestFactory().get('v1/api/bugs', HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'get': 'retrieve'})(request, pk=new_bug.id)

        json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 404)

    def test_get_bug_with_token_from_my_user(self):
        user = self.create_user('my_username', False)
        new_bug = self.create_bug(user)
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().get('v1/api/bugs', HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'get': 'retrieve'})(request, pk=new_bug.id)

        response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(response['title'], 'Bug')

    def test_get_bug_with_token_deactivated(self):
        user = self.create_user(False)
        self.create_bug(user, 'DEACTIVATE')
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().get('v1/api/bugs', HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'get': 'list'})(request)

        bug_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug_response['count'], 0)

    def test_post_bug_without_token(self):
        data = {
                'title': 'Bug',
                'description': 'description',
                'priority': 'cpriority'
        }

        request = RequestFactory().post('v1/api/bugs', data=data)

        request.user = AnonymousUser()
        resp = BugViewSet.as_view({'get': 'list'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_post_bug_with_token(self):
        user = self.create_user(False)
        data = {
                'title': 'Bug',
                'description': 'description',
                'priority': 'cpriority'
        }

        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().post('v1/api/bugs', data=data, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(json.loads(json.dumps(resp.data))['title'], 'Bug')

    def test_delete_bug_without_token(self):
        user = self.create_user(False)
        self.create_bug(user)
        bug = self.create_bug(user)
        request = RequestFactory().delete('v1/api/bugs/', pk=bug.id)
        request.user = AnonymousUser()
        resp = BugViewSet.as_view({'delete': 'destroy'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')
        self.assertEqual(bug.status, 'NEW')

    def test_delete_bug_with_token(self):
        user = self.create_user(False)
        new_bug = self.create_bug(user)
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().delete('v1/api/bugs/', HTTP_AUTHORIZATION=token.key, pk=new_bug.id)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'delete': 'destroy'})(request, pk=new_bug.id)
        bug = json.loads(serializers.serialize('json', Bug.objects.filter(author=user, pk=new_bug.id)))[0]['fields']

        self.assertEqual(resp.status_code, 202)
        self.assertEqual(bug['status'], 'DEACTIVATE')

    def test_delete_bug_with_token_from_another_user(self):
        user = self.create_user(False)
        user2 = self.create_user('user2', False)
        new_bug = self.create_bug(user)
        token = self.create_token(user2)
        token.generate_key()
        request = RequestFactory().delete('v1/api/bugs/', HTTP_AUTHORIZATION=token.key, pk=new_bug.id)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'delete': 'destroy'})(request, pk=new_bug.id)

        self.assertEqual(resp.status_code, 404)

    def test_put_bug_without_token(self):
        user = self.create_user(False)
        new_bug = self.create_bug(user)
        data = {
                'title': 'Bug_update',
                'description': 'description_update',
                'priority': 'cpriority_update'
        }

        request = RequestFactory().put('v1/api/bugs', data=data, pk=new_bug.id)

        request.user = AnonymousUser()
        resp = BugViewSet.as_view({'put': 'update'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_update_bug_with_token(self):
        user = self.create_user(False)
        new_bug = self.create_bug(user)
        token = self.create_token(user)
        data = {
                'title': 'Bug_update',
                'description': 'description_update',
                'priority': 'cpriority_update'
        }

        request = RequestFactory().put('v1/api/bugs', data=data, pk=new_bug.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'put': 'update'})(request, pk=new_bug.id)
        bug = json.loads(serializers.serialize('json', Bug.objects.filter(author=user, pk=new_bug.id)))[0]['fields']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug['title'], 'Bug_update')
        self.assertEqual(json.loads(json.dumps(resp.data))['title'], 'Bug_update')

    def test_update_bug_with_token_from_another_user(self):
        user = self.create_user(False)
        user2 = self.create_user('user2', False)
        new_bug = self.create_bug(user)
        token = self.create_token(user2)
        token.generate_key()
        data = {
                'title': 'Bug_update',
                'description': 'description_update',
                'priority': 'cpriority_update'
        }

        request = RequestFactory().put('v1/api/bugs', data=data, pk=new_bug.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'put': 'update'})(request, pk=new_bug.id)

        self.assertEqual(resp.status_code, 404)

    def test_patch_bug_with_token(self):
        user = self.create_user(False)
        user2 = self.create_user('user2', False)
        new_bug = self.create_bug(user)
        token = self.create_token(user2)
        token.generate_key()
        data = {
                'title': 'Bug_update',
                'description': 'description_update',
                'priority': 'cpriority_update'
        }

        request = RequestFactory().put('v1/api/bugs', data=data, pk=new_bug.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'patch': 'partial_update'})(request, pk=new_bug.id)

        self.assertEqual(resp.status_code, 403)

    def test_options_bug_with_token(self):
        user = self.create_user(False)
        user2 = self.create_user('user2', False)
        new_bug = self.create_bug(user)
        token = self.create_token(user2)
        token.generate_key()
        data = {
                'title': 'Bug_update',
                'description': 'description_update',
                'priority': 'cpriority_update'
        }

        request = RequestFactory().options('v1/api/bugs', data=data, pk=new_bug.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'options': 'partial_update'})(request, pk=new_bug.id)

        self.assertEqual(resp.status_code, 403)

    @staticmethod
    def create_bug(user, status='NEW'):
        return Bug.objects.create(title='Bug', description='description', priority='HIGH', status=status, author=user)

    @staticmethod
    def create_user(user='username', root=False):
        return User.objects.create(username=user, password='password', email='email', is_superuser=root)

    @staticmethod
    def create_token(user):
        return Token.objects.create(user=user)
