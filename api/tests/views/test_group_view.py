from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate
from rest_framework.utils import json

from api.tests.data_factory import FactoryData
from api.views.group_view import GroupViewSet

API_GROUPS = 'api/v1/groups'


class GroupViewTest(TestCase):

    def test_get_group_without_token(self):
        FactoryData.create_user(False)
        FactoryData.create_group()
        request = RequestFactory().get(API_GROUPS)
        request.user = AnonymousUser()
        resp = GroupViewSet.as_view({'get': 'list'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_get_group_with_token_without_super(self):
        user = FactoryData.create_user(False)
        FactoryData.create_group()
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_GROUPS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'get': 'list'})(request)

        bug_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug_response['count'], 0)

    def test_get_group_with_token_with_super(self):
        user = FactoryData.create_user('user2', True)
        group = FactoryData.create_group()
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_GROUPS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'get': 'list'})(request)

        user_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['count'], 1)
        self.assertEqual(user_response['results'][0]['name'], group.name)

    def test_retrieve_group_with_super(self):
        user = FactoryData.create_user('user2', True)
        group = FactoryData.create_group()
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_GROUPS, pk=group.id, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'get': 'retrieve'})(request, pk=group.id)

        response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(response['name'], group.name)

    def test_get_bug_with_token_without_super(self):
        user = FactoryData.create_user('user2', False)
        group = FactoryData.create_group()
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_GROUPS, pk=group.id, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'get': 'retrieve'})(request, pk=group.id)

        json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 404)

    def test_post_group_without(self):
        data = {
                'name': 'Group',
        }

        request = RequestFactory().post(API_GROUPS, data=data,  content_type='application/json')
        request.user = AnonymousUser()
        resp = GroupViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_post_group_with_token_with_super(self):
        data = {
                'name': 'Group',
        }
        user = FactoryData.create_user('user2', True)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().post(API_GROUPS, data=data,  HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(json.loads(json.dumps(resp.data))['id'], 1)

    def test_post_group_with_token_without_super(self):
        data = {
                'name': 'Group',
        }
        user = FactoryData.create_user('user2', False)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().post(API_GROUPS, data=data,  HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 401)

    def test_put_group_with_token(self):
        user = FactoryData.create_user(True)
        token = FactoryData.create_token(user)
        group = FactoryData.create_group()
        token.generate_key()
        data = {
                'name': 'Group',
        }

        request = RequestFactory().patch(API_GROUPS, data=data, pk=group.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'put': 'update'})(request, pk=group.id)

        self.assertEqual(resp.status_code, 403)

    def test_patch_group_with_token(self):
        user = FactoryData.create_user(True)
        token = FactoryData.create_token(user)
        group = FactoryData.create_group()
        token.generate_key()
        data = {
                'name': 'Group',
        }

        request = RequestFactory().patch(API_GROUPS, data=data, pk=group.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'patch': 'partial_update'})(request, pk=group.id)

        self.assertEqual(resp.status_code, 405)

    def test_options_user_with_token(self):
        user = FactoryData.create_user(True)
        token = FactoryData.create_token(user)
        group = FactoryData.create_group()
        token.generate_key()
        data = {
                'name': 'Group',
        }

        request = RequestFactory().options(API_GROUPS, data=data, pk=group.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'options': 'partial_update'})(request, pk=group.id)

        self.assertEqual(resp.status_code, 403)

    def test_delete_user_with_token(self):
        user = FactoryData.create_user(True)
        token = FactoryData.create_token(user)
        group = FactoryData.create_group()
        token.generate_key()

        request = RequestFactory().delete(API_GROUPS, pk=group.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = GroupViewSet.as_view({'delete': 'destroy'})(request, pk=group.id)

        self.assertEqual(resp.status_code, 405)


