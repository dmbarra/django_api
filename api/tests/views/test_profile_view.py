from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate
from rest_framework.utils import json

from api.tests.data_factory import FactoryData
from api.views.profile_view import ProfileViewSet

API_PROFILE = 'api/v1/users/{user.id}/profile'
API_USERS = 'api/v1/users/'


class ProfileViewTest(TestCase):

    def test_get_profile_without_token(self):
        request = RequestFactory().get(API_USERS)
        request.user = AnonymousUser()
        resp = ProfileViewSet.as_view({'get': 'list'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_get_profile_with_token_not_superuser(self):
        user = FactoryData.create_user('qa_user')
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_USERS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = ProfileViewSet.as_view({'get': 'list'})(request)

        self.assertEqual(resp.status_code, 403)

    def test_get_profile_with_token_and_superuser(self):
        user = FactoryData.create_user('user', True)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_PROFILE, HTTP_AUTHORIZATION=token.key, user_pk=user.id)
        force_authenticate(request, user=user, token=token)
        resp = ProfileViewSet.as_view({'get': 'list'})(request, user_pk=user.id)
        profile_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(profile_response['count'], 1)
        self.assertContains(resp, 'total_bugs')
        self.assertContains(resp, 'active_bugs')
        self.assertContains(resp, 'last_login')
        self.assertContains(resp, 'date_joined')
        self.assertContains(resp, 'total_logins')
        self.assertContains(resp, 'total_tasks')
        self.assertContains(resp, 'total_subtasks')

    def test_get_profile_with_created_bugs_and_deleted_bugs(self):
        user = FactoryData.create_user('user', True)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_PROFILE, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)

        FactoryData.create_bug(user, 'NEW')
        FactoryData.create_bug(user, 'UPDATED')
        FactoryData.create_bug(user, 'DELETED')

        resp = ProfileViewSet.as_view({'get': 'list'})(request, user_pk=user.id)
        profile_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(profile_response['results'][0]['total_bugs'], 3)
        self.assertEqual(profile_response['results'][0]['active_bugs'], 2)
