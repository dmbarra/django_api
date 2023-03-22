from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate
from rest_framework.utils import json
from django.core import serializers

from api.models.bug_model import Bug
from api.models.choices.status_choices import Status
from api.tests.data_factory import FactoryData
from api.views.bug_view import BugViewSet

API_BUGS = 'api/v1/bugs'


class BugViewTest(TestCase):

    def test_get_bug_without_token(self):
        user = FactoryData.create_user(False)
        FactoryData.create_bug(user)
        request = RequestFactory().get(API_BUGS)
        request.user = AnonymousUser()
        resp = BugViewSet.as_view({'get': 'list'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_get_bug_with_token(self):
        user = FactoryData.create_user(False)
        bug = FactoryData.create_bug(user)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_BUGS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'get': 'list'})(request)

        bug_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug_response['count'], 1)
        self.assertEqual(bug_response['results'][0]['title'], bug.title)

    def test_get_bug_with_token_from_another_user(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        FactoryData.create_bug(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        request = RequestFactory().get(API_BUGS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'get': 'list'})(request)

        bug_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug_response['count'], 0)

    def test_retrieve_bug_with_token_from_another_user(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        new_bug = FactoryData.create_bug(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        request = RequestFactory().get(API_BUGS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'get': 'retrieve'})(request, pk=new_bug.id)

        json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 404)

    def test_get_bug_with_token_from_my_user(self):
        user = FactoryData.create_user('my_username', False)
        new_bug = FactoryData.create_bug(user)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_BUGS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'get': 'retrieve'})(request, pk=new_bug.id)

        response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(response['title'], 'Bug')

    def test_get_bug_with_token_deactivated_status(self):
        user = FactoryData.create_user(False)
        FactoryData.create_bug(user, Status.DELETED)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_BUGS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'get': 'list'})(request)

        bug_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug_response['count'], 0)

    def test_post_bug_without_token(self):
        data = {
                'title': 'Bug',
                'description': 'description',
                'priority': 'HIGH'
        }

        request = RequestFactory().post(API_BUGS, data=data)

        request.user = AnonymousUser()
        resp = BugViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_post_bug_with_token(self):
        user = FactoryData.create_user(False)
        data = {
                'title': 'Bug',
                'description': 'description',
                'priority': 'LOW'
        }

        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().post(API_BUGS, data=data, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(json.loads(json.dumps(resp.data))['title'], 'Bug')

    def test_delete_bug_without_token(self):
        user = FactoryData.create_user(False)
        FactoryData.create_bug(user)
        bug = FactoryData.create_bug(user)
        request = RequestFactory().delete(API_BUGS, pk=bug.id)
        request.user = AnonymousUser()
        resp = BugViewSet.as_view({'delete': 'destroy'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')
        self.assertEqual(bug.status, 'NEW')

    def test_delete_bug_with_token(self):
        user = FactoryData.create_user(False)
        new_bug = FactoryData.create_bug(user)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().delete(API_BUGS, HTTP_AUTHORIZATION=token.key, pk=new_bug.id)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'delete': 'destroy'})(request, pk=new_bug.id)
        bug = json.loads(serializers.serialize('json', Bug.objects.filter(author=user, pk=new_bug.id)))[0]['fields']

        self.assertEqual(resp.status_code, 202)
        self.assertEqual(bug['status'], Status.DELETED)

    def test_delete_bug_with_token_from_another_user(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        new_bug = FactoryData.create_bug(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        request = RequestFactory().delete(API_BUGS, HTTP_AUTHORIZATION=token.key, pk=new_bug.id)
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'delete': 'destroy'})(request, pk=new_bug.id)

        self.assertEqual(resp.status_code, 404)

    def test_partially_update_bug_without_token(self):
        user = FactoryData.create_user(False)
        new_bug = FactoryData.create_bug(user)
        data = {
                'title': 'Bug_update',
                'description': 'description_update',
                'priority': 'HIGH'
        }

        request = RequestFactory().patch(API_BUGS, data=data, pk=new_bug.id)

        request.user = AnonymousUser()
        resp = BugViewSet.as_view({'patch': 'partial_update'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_partially_update_bug_with_token(self):
        user = FactoryData.create_user(False)
        new_bug = FactoryData.create_bug(user)
        token = FactoryData.create_token(user)
        data = {
                'title': 'Bug_update',
                'description': 'description_update',
                'priority': 'MEDIUM'
        }

        request = RequestFactory().patch(API_BUGS, data=data, pk=new_bug.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'patch': 'partial_update'})(request, pk=new_bug.id)
        bug = json.loads(serializers.serialize('json', Bug.objects.filter(author=user, pk=new_bug.id)))[0]['fields']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug['title'], 'Bug_update')
        self.assertEqual(json.loads(json.dumps(resp.data))['title'], 'Bug_update')

    def test_partially_update_bug_with_token_from_another_user(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        new_bug = FactoryData.create_bug(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        data = {
                'title': 'Bug_update',
                'description': 'description_update',
                'priority': 'MEDIUM'
        }

        request = RequestFactory().patch(API_BUGS, data=data, pk=new_bug.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'patch': 'partial_update'})(request, pk=new_bug.id)

        self.assertEqual(resp.status_code, 404)

    def test_update_bug_with_token(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        new_bug = FactoryData.create_bug(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        data = {
                'title': 'Bug_update',
                'description': 'description_update',
                'priority': 'cpriority_update'
        }

        request = RequestFactory().put(API_BUGS, data=data, pk=new_bug.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'put': 'update'})(request, pk=new_bug.id)

        self.assertEqual(resp.status_code, 405)

    def test_options_bug_with_token(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        new_bug = FactoryData.create_bug(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        data = {
                'title': 'Bug_update',
                'description': 'description_update',
                'priority': 'cpriority_update'
        }

        request = RequestFactory().options(API_BUGS, data=data, pk=new_bug.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = BugViewSet.as_view({'options': 'partial_update'})(request, pk=new_bug.id)

        self.assertEqual(resp.status_code, 403)


