from django.contrib.auth.models import AnonymousUser, User, Group
from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate
from rest_framework.utils import json

from api.tests.data_factory import FactoryData
from api.views.user_view import UserViewSet

API_USERS = 'api/v1/users'


class UserViewTest(TestCase):

    def test_get_user_without_token(self):
        FactoryData.create_user(False)
        request = RequestFactory().get(API_USERS)
        request.user = AnonymousUser()
        resp = UserViewSet.as_view({'get': 'list'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_get_user_with_token_without_super(self):
        user = FactoryData.create_user()
        FactoryData.create_user('user2', False)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_USERS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'get': 'list'})(request)

        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['count'], 1)
        self.assertEqual(user_response['results'][0]['username'], user.username)
        self.assertEqual(user_response['results'][0]['name'], user.first_name)
        self.assertEqual(user_response['results'][0]['email'], user.email)

    def test_get_user_with_token_with_super(self):
        user = FactoryData.create_user('user', True)
        FactoryData.create_user('user2')
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_USERS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'get': 'list'})(request)

        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['count'], 2)

    def test_retrieve_user_without_token(self):
        user = FactoryData.create_user(False)
        request = RequestFactory().get(API_USERS)
        request.user = AnonymousUser()
        resp = UserViewSet.as_view({'get': 'retrieve'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_retrieve_user_with_token_without_super(self):
        user = FactoryData.create_user()
        FactoryData.create_user('user2', False)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_USERS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'get': 'retrieve'})(request, pk=user.id)

        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['username'], user.username)

    def test_post_user(self):
        data = {
                'username': 'User',
                'email': 'email@email.com',
                'password': 'cpriority',
                'name': 'Roberto'
        }

        request = RequestFactory().post(API_USERS, data=data, content_type='application/json')
        request.user = AnonymousUser()
        resp = UserViewSet.as_view({'post': 'create'})(request)

        user_data = User.objects.get(pk=json.loads(json.dumps(resp.data))['id'])

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(json.loads(json.dumps(resp.data))['id'], 1)
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data.username, 'User')
        self.assertEqual(user_data.email, 'email@email.com')
        self.assertIsNotNone(user_data.password)
        self.assertEqual(user_data.first_name, 'Roberto')
        self.assertIn(user_data, Group.objects.get(name='candidates').user_set.all())

    def test_partially_update_user_without_token(self):
        data = {
                'username': 'User_updated',
                'email': 'email_updated@email.com',
                'password': 'cpriority_updated',
                'name': 'updated_name'
        }
        user = FactoryData.create_user(False)
        request = RequestFactory().patch(API_USERS, data=data, pk=user.id, content_type='application/json')
        request.user = AnonymousUser()
        resp = UserViewSet.as_view({'patch': 'partial_update'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_partially_update_user_with_token(self):
        data = {
                'name': 'User_updated',
        }
        user = FactoryData.create_user()
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().patch(API_USERS, data=data, pk=user.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'patch': 'partial_update'})(request, pk=user.id)

        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['name'], 'User_updated')

    def test_partially_update_user_with_token_from_another_user(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        token = FactoryData.create_token(user2)
        token.generate_key()
        data = {
                'username': 'User_updated',
                'email': 'email_updated@email.com',
                'password': 'cpriority_updated',
                'name': 'updated_name'
        }

        request = RequestFactory().patch(API_USERS, data=data, pk=user.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'patch': 'partial_update'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 404)

    def test_update_user_with_token(self):
        user = FactoryData.create_user(False)
        token = FactoryData.create_token(user)
        token.generate_key()
        data = {
                'username': 'User_updated',
                'email': 'email_updated@email.com',
                'password': 'cpriority_updated'
        }

        request = RequestFactory().put(API_USERS, data=data, pk=user.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'put': 'update'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 405)

    def test_options_user_with_token(self):
        user = FactoryData.create_user(False)
        token = FactoryData.create_token(user)
        token.generate_key()
        data = {
                'username': 'User_updated',
                'email': 'email_updated@email.com',
                'password': 'cpriority_updated'
        }

        request = RequestFactory().options(API_USERS, data=data, pk=user.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'options': 'options'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 403)

    def test_delete_user_with_token(self):
        user = FactoryData.create_user(False)
        token = FactoryData.create_token(user)
        token.generate_key()
        data = {
                'username': 'User_updated',
                'email': 'email_updated@email.com',
                'password': 'cpriority_updated'
        }

        request = RequestFactory().delete(API_USERS, pk=user.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = UserViewSet.as_view({'delete': 'destroy'})(request, pk=user.id)

        self.assertEqual(resp.status_code, 405)

    def test_search_user_by_email(self):
        user = FactoryData.create_user('user', True)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_USERS, {'search': user.email}, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)

        resp = UserViewSet.as_view({'get' : 'list'})(request)
        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['count'], 1)

    def test_search_user_by_username(self):
        user = FactoryData.create_user('user', True)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_USERS, {'search': user.username}, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)

        resp = UserViewSet.as_view({'get' : 'list'})(request)
        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['count'], 1)




