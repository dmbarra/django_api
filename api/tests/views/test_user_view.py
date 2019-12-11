from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate
from rest_framework.utils import json

from api.views.user_view import UserViewSet


class UserViewTest(TestCase):

    def test_get_user_without_token(self):
        self.create_user(False)
        request = RequestFactory().get('v1/api/users')
        request.user = AnonymousUser()
        resp = UserViewSet.as_view({'get': 'list'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_get_user_with_token_without_super(self):
        user = self.create_user()
        self.create_user('user2', False)
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().get('v1/api/users', HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'get': 'list'})(request)

        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['count'], 1)
        self.assertEqual(user_response['results'][0]['username'], user.username)

    def test_get_user_with_token_with_super(self):
        user = self.create_user('user', True)
        self.create_user('user2')
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().get('v1/api/users', HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'get': 'list'})(request)

        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['count'], 2)

    def test_retrieve_user_without_token(self):
        user = self.create_user(False)
        request = RequestFactory().get('v1/api/users')
        request.user = AnonymousUser()
        resp = UserViewSet.as_view({'get': 'retrieve'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_retrieve_user_with_token_without_super(self):
        user = self.create_user()
        self.create_user('user2', False)
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().get('v1/api/users', HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'get': 'retrieve'})(request, pk=user.id)

        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['username'], user.username)

    def test_post_user(self):
        data = {
                'username': 'User',
                'email': 'email@email.com',
                'password': 'cpriority'
        }

        request = RequestFactory().post('v1/api/users', data=data, content_type='application/json')
        request.user = AnonymousUser()
        resp = UserViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(json.loads(json.dumps(resp.data))['id'], 1)

    def test_update_user_without_token(self):
        data = {
                'username': 'User_updated',
                'email': 'email_updated@email.com',
                'password': 'cpriority_updated'
        }
        user = self.create_user(False)
        request = RequestFactory().put('v1/api/users', data=data, pk=user.id, content_type='application/json')
        request.user = AnonymousUser()
        resp = UserViewSet.as_view({'put': 'update'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_update_user_with_token(self):
        data = {
                'username': 'User_updated',
                'email': 'email_updated@email.com',
                'password': 'cpriority_updated'
        }
        user = self.create_user()
        token = self.create_token(user)
        token.generate_key()
        request = RequestFactory().put('v1/api/users', data=data, pk=user.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'put': 'update'})(request, pk=user.id)

        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['username'], 'User_updated')

    def test_update_user_with_token_from_another_user(self):
        user = self.create_user(False)
        user2 = self.create_user('user2', False)
        token = self.create_token(user2)
        token.generate_key()
        data = {
                'username': 'User_updated',
                'email': 'email_updated@email.com',
                'password': 'cpriority_updated'
        }

        request = RequestFactory().put('v1/api/users', data=data, pk=user.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'put': 'update'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 404)

    def test_patch_user_with_token(self):
        user = self.create_user(False)
        token = self.create_token(user)
        token.generate_key()
        data = {
                'username': 'User_updated',
                'email': 'email_updated@email.com',
                'password': 'cpriority_updated'
        }

        request = RequestFactory().patch('v1/api/users', data=data, pk=user.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'patch': 'partial_update'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 405)

    def test_options_user_with_token(self):
        user = self.create_user(False)
        token = self.create_token(user)
        token.generate_key()
        data = {
                'username': 'User_updated',
                'email': 'email_updated@email.com',
                'password': 'cpriority_updated'
        }

        request = RequestFactory().options('v1/api/users', data=data, pk=user.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'options': 'partial_update'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 403)

    def test_delete_user_with_token(self):
        user = self.create_user(False)
        token = self.create_token(user)
        token.generate_key()
        data = {
                'username': 'User_updated',
                'email': 'email_updated@email.com',
                'password': 'cpriority_updated'
        }

        request = RequestFactory().delete('v1/api/users', data=data, pk=user.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'delete': 'destroy'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 405)

    @staticmethod
    def create_user(user='username', root=False):
        return User.objects.create(username=user, password='password', email='email', is_superuser=root)

    @staticmethod
    def create_token(user):
        return Token.objects.create(user=user)



