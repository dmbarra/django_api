from django.contrib.auth.models import User, Group, AnonymousUser
from django.test import TestCase, RequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate
from rest_framework.utils import json

from api.views.group_view import GroupViewSet


class GroupViewTest(TestCase):

    def test_get_group_without_token(self):
        self.create_user(False)
        self.create_group()
        request = RequestFactory().get('v1/api/groups')
        request.user = AnonymousUser()
        resp = GroupViewSet.as_view({'get': 'list'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_get_group_with_token_without_super(self):
        user = self.create_user(False)
        self.create_group()
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().get('v1/api/groups', HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'get': 'list'})(request)

        bug_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug_response['count'], 0)

    def test_get_group_with_token_with_super(self):
        user = self.create_user('user2', True)
        group = self.create_group()
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().get('v1/api/groups', HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'get': 'list'})(request)

        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['count'], 1)
        self.assertEqual(user_response['results'][0]['name'], group.name)

    def test_retrieve_group_with_super(self):
        user = self.create_user('user2', True)
        group = self.create_group()
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().get('v1/api/groups', pk=group.id, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'get': 'retrieve'})(request, pk=group.id)

        response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(response['name'], group.name)

    def test_get_bug_with_token_without_super(self):
        user = self.create_user('user2', False)
        group = self.create_group()
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().get('v1/api/groups', pk=group.id, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'get': 'retrieve'})(request, pk=group.id)

        json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 404)

    def test_post_group_without(self):
        data = {
                'name': 'Group',
        }

        request = RequestFactory().post('v1/api/groups', data=data,  content_type='application/json')
        request.user = AnonymousUser()
        resp = GroupViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_post_group_with_token_with_super(self):
        data = {
                'name': 'Group',
        }
        user = self.create_user('user2', True)
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().post('v1/api/groups', data=data,  HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(json.loads(json.dumps(resp.data))['id'], 1)

    def test_post_group_with_token_without_super(self):
        data = {
                'name': 'Group',
        }
        user = self.create_user('user2', False)
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().post('v1/api/groups', data=data,  HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 401)

    def test_put_group_with_token(self):
        user = self.create_user(True)
        token = self.create_token(user)
        group = self.create_group()
        token.generate_key()
        data = {
                'name': 'Group',
        }

        request = RequestFactory().patch('v1/api/groups', data=data, pk=group.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'put': 'update'})(request, pk=group.id)

        self.assertEqual(resp.status_code, 403)

    def test_patch_group_with_token(self):
        user = self.create_user(True)
        token = self.create_token(user)
        group = self.create_group()
        token.generate_key()
        data = {
                'name': 'Group',
        }

        request = RequestFactory().patch('v1/api/groups', data=data, pk=group.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'patch': 'partial_update'})(request, pk=group.id)

        self.assertEqual(resp.status_code, 405)

    def test_options_user_with_token(self):
        user = self.create_user(True)
        token = self.create_token(user)
        group = self.create_group()
        token.generate_key()
        data = {
                'name': 'Group',
        }

        request = RequestFactory().options('v1/api/groups', data=data, pk=group.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'options': 'partial_update'})(request, pk=group.id)

        self.assertEqual(resp.status_code, 403)

    def test_delete_user_with_token(self):
        user = self.create_user(True)
        token = self.create_token(user)
        group = self.create_group()
        token.generate_key()

        request = RequestFactory().delete('v1/api/groups', pk=group.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'delete': 'destroy'})(request, pk=group.id)

        self.assertEqual(resp.status_code, 405)

    @staticmethod
    def create_user(user='username', root=False):
        return User.objects.create(username=user, password='password', email='email', is_superuser=root)

    @staticmethod
    def create_token(user):
        return Token.objects.create(user=user)

    @staticmethod
    def create_group(group='default'):
        return Group.objects.create(name=group)
