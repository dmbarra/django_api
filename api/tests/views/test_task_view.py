from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.core import serializers
from rest_framework.test import force_authenticate
from rest_framework.utils import json

from api.models.task_model import Task
from api.tests.data_factory import FactoryData
from api.views.task_view import TaskViewSet

API_TASKS = 'api/v1/tasks'


class TaskViewTest(TestCase):

    def test_get_task_without_token(self):
        user = FactoryData.create_user(False)
        FactoryData.create_task(user)
        request = RequestFactory().get(API_TASKS)
        request.user = AnonymousUser()
        resp = TaskViewSet.as_view({'get': 'list'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_get_task_with_token(self):
        user = FactoryData.create_user(False)
        task = FactoryData.create_task(user)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_TASKS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'get': 'list'})(request)

        task_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(task_response['count'], 1)
        self.assertEqual(task_response['results'][0]['body'], task.body)

    def test_get_task_with_token_from_another_user(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        FactoryData.create_task(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        request = RequestFactory().get(API_TASKS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'get': 'list'})(request)

        bug_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug_response['count'], 0)

    def test_retrieve_task_with_token_from_another_user(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        new_task = FactoryData.create_task(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        request = RequestFactory().get(API_TASKS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user2, token=token)
        resp = TaskViewSet.as_view({'get': 'retrieve'})(request, pk=new_task.id)

        json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 404)

    def test_get_task_with_token_from_my_user(self):
        user = FactoryData.create_user('my_username', False)
        new_task = FactoryData.create_task(user)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_TASKS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'get': 'retrieve'})(request, pk=new_task.id)

        response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(response['body'], new_task.body)

    def test_get_task_with_token_deactivated_status(self):
        user = FactoryData.create_user(False)
        FactoryData.create_task(user, 'DEACTIVATE')
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_TASKS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'get': 'list'})(request)

        bug_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug_response['count'], 0)

    def test_post_task_without_token(self):
        data = {
                'body': 'Task body message'
        }

        request = RequestFactory().post(API_TASKS, data=data)

        request.user = AnonymousUser()
        resp = TaskViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_post_task_with_token(self):
        user = FactoryData.create_user(False)
        data = {
                'body': 'Task body message'
        }

        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().post(API_TASKS, data=data, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(json.loads(json.dumps(resp.data))['body'], 'Task body message')

    def test_delete_task_without_token(self):
        user = FactoryData.create_user(False)
        FactoryData.create_task(user)
        task = FactoryData.create_task(user)
        request = RequestFactory().delete(API_TASKS, pk=task.id)
        request.user = AnonymousUser()
        resp = TaskViewSet.as_view({'delete': 'destroy'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')
        self.assertEqual(task.status, 'NEW')

    def test_delete_task_with_token(self):
        user = FactoryData.create_user(False)
        new_task = FactoryData.create_task(user)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().delete(API_TASKS, HTTP_AUTHORIZATION=token.key, pk=new_task.id)
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'delete': 'destroy'})(request, pk=new_task.id)
        bug = json.loads(serializers.serialize('json', Task.objects.filter(author=user, pk=new_task.id)))[0]['fields']

        self.assertEqual(resp.status_code, 202)
        self.assertEqual(bug['status'], 'DELETED')

    def test_delete_task_with_token_from_another_user(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        new_task = FactoryData.create_task(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        request = RequestFactory().delete(API_TASKS, HTTP_AUTHORIZATION=token.key, pk=new_task.id)
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'delete': 'destroy'})(request, pk=new_task.id)

        self.assertEqual(resp.status_code, 404)

    def test_partial_update_task_without_token(self):
        user = FactoryData.create_user(False)
        new_task = FactoryData.create_task(user)
        data = {
            'body': 'Task body message updated'
        }

        request = RequestFactory().patch(API_TASKS, data=data, pk=new_task.id)

        request.user = AnonymousUser()
        resp = TaskViewSet.as_view({'patch': 'partial_update'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_partial_update_task_with_token(self):
        user = FactoryData.create_user(False)
        new_task = FactoryData.create_task(user)
        token = FactoryData.create_token(user)
        data = {
            'body': 'Task body message updated'
        }

        request = RequestFactory().patch(API_TASKS, data=data, pk=new_task.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'patch': 'partial_update'})(request, pk=new_task.id)
        task = json.loads(serializers.serialize('json', Task.objects.filter(author=user, pk=new_task.id)))[0]['fields']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(task['body'], 'Task body message updated')
        self.assertEqual(json.loads(json.dumps(resp.data))['body'], 'Task body message updated')
        self.assertEqual(task['status'], 'UPDATED')

    def test_partial_update_task_with_token_from_another_user(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        new_bug = FactoryData.create_task(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        data = {
            'body': 'Task body message updated'
        }

        request = RequestFactory().patch(API_TASKS, data=data, pk=new_bug.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'patch': 'partial_update'})(request, pk=new_bug.id)

        self.assertEqual(resp.status_code, 404)

    def test_update_bug_with_token(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        new_task = FactoryData.create_task(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        data = {
            'body': 'Task body message updated'
        }

        request = RequestFactory().put(API_TASKS, data=data, pk=new_task.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'put': 'update'})(request, pk=new_task.id)

        self.assertEqual(resp.status_code, 405)

    def test_options_bug_with_token(self):
        user = FactoryData.create_user(False)
        user2 = FactoryData.create_user('user2', False)
        new_task = FactoryData.create_task(user)
        token = FactoryData.create_token(user2)
        token.generate_key()
        data = {
            'body': 'Task body message updated'
        }

        request = RequestFactory().options(API_TASKS, data=data, pk=new_task.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'options': 'partial_update'})(request, pk=new_task.id)

        self.assertEqual(resp.status_code, 403)

    def test_task_total_subtask(self):
        user = FactoryData.create_user(False)
        task = FactoryData.create_task(user)
        subtask = FactoryData.create_sub_task(task)

        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_TASKS, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = TaskViewSet.as_view({'get': 'retrieve'})(request, pk=task.id)

        response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(response['total_subtasks'], 1)
