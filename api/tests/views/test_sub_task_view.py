from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.core import serializers
from rest_framework.test import force_authenticate
from rest_framework.utils import json

from api.models.sub_task_model import SubTask
from api.tests.data_factory import FactoryData
from api.views.sub_task_view import SubTaskViewSet

API_TASKS = 'api/v1/tasks/'
API_SUB_TASK = '/subtasks'


class SubTaskViewTest(TestCase):

    def test_get_sub_task_without_token(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        FactoryData.create_sub_task(task)
        request = RequestFactory().get(API_TASKS + str(task.pk) + API_SUB_TASK)
        request.user = AnonymousUser()
        resp = SubTaskViewSet.as_view({'get': 'list'})(request)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_get_sub_task_with_token(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        sub_task = FactoryData.create_sub_task(task)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_TASKS + str(task.pk) + API_SUB_TASK, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = SubTaskViewSet.as_view({'get': 'list'})(request, task_pk=task.id)

        task_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(task_response['count'], 1)
        self.assertEqual(task_response['results'][0]['description'], sub_task.description)

    def test_get_task_with_token_from_another_user(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        FactoryData.create_sub_task(task)

        user2 = FactoryData.create_user('user2', False)
        token = FactoryData.create_token(user2)
        token.generate_key()
        request = RequestFactory().get(API_TASKS + str(task.pk) + API_SUB_TASK, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user2, token=token)
        resp = SubTaskViewSet.as_view({'get': 'list'})(request, task_pk=task.id)

        json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 404)

    def test_get_sub_task_with_token_from_another_user(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)

        user2 = FactoryData.create_user('user2', False)
        task2 = FactoryData.create_task(user2)
        FactoryData.create_sub_task(task2)

        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_TASKS + str(task.pk) + API_SUB_TASK, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = SubTaskViewSet.as_view({'get': 'list'})(request, task_pk=task.id)

        task_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(task_response['count'], 0)

    def test_retrieve_sub_task_with_token_from_another_user(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        FactoryData.create_sub_task(task)

        user2 = FactoryData.create_user('user2', False)
        task2 = FactoryData.create_task(user2)
        sub_task2 = FactoryData.create_sub_task(task2)

        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_TASKS + str(task.pk) + API_SUB_TASK, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = SubTaskViewSet.as_view({'get': 'retrieve'})(request, task_pk=task.id, pk=sub_task2.id)

        json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 404)

    def test_get_sub_task_with_token_from_my_user(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        sub_task = FactoryData.create_sub_task(task)

        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_TASKS + str(task.pk) + API_SUB_TASK, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = SubTaskViewSet.as_view({'get': 'retrieve'})(request, task_pk=task.id, pk=sub_task.id)

        response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(response['description'], sub_task.description)

    def test_get_sub_task_with_token_deactivated_status(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        FactoryData.create_sub_task(task, 'DEACTIVATE')

        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().get(API_TASKS + str(task.pk) + API_SUB_TASK, HTTP_AUTHORIZATION=token.key)
        force_authenticate(request, user=user, token=token)
        resp = SubTaskViewSet.as_view({'get': 'list'})(request, task_pk=task.id)

        bug_response = json.loads(json.dumps(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(bug_response['count'], 0)

    def test_post_sub_task_without_token(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        data = {
                'description': 'Task body message'
        }

        request = RequestFactory().post(API_TASKS + str(task.pk) + API_SUB_TASK, data=data)

        request.user = AnonymousUser()
        resp = SubTaskViewSet.as_view({'post': 'create'})(request, task_pk=task.id)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_post_sub_task_with_token(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        data = {
                'description': 'Sub Task body message',
                'due_date': '2019-09-22T00:00:00'
        }

        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().post(API_TASKS + str(task.pk) + API_SUB_TASK, data=data, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = SubTaskViewSet.as_view({'post': 'create'})(request, task_pk=task.id)

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(json.loads(json.dumps(resp.data))['description'], 'Sub Task body message')

    def test_delete_sub_task_without_token(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        sub_task = FactoryData.create_sub_task(task)
        request = RequestFactory().delete(API_TASKS + str(task.pk) + API_SUB_TASK, pk=sub_task.id)
        request.user = AnonymousUser()
        resp = SubTaskViewSet.as_view({'delete': 'destroy'})(request, task_pk=task.id, pk=sub_task.id)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')
        self.assertEqual(sub_task.status, 'NEW')

    def test_delete_sub_task_with_token(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        sub_task = FactoryData.create_sub_task(task)
        token = FactoryData.create_token(user)
        token.generate_key()
        request = RequestFactory().delete(API_TASKS + str(task.pk) + API_SUB_TASK, HTTP_AUTHORIZATION=token.key, pk=sub_task.id)
        force_authenticate(request, user=user, token=token)
        resp = SubTaskViewSet.as_view({'delete': 'destroy'})(request, task_pk=task.id, pk=sub_task.id)
        sub_task_json = json.loads(serializers.serialize('json', SubTask.objects.filter(task=task, pk=sub_task.id)))[0]['fields']

        self.assertEqual(resp.status_code, 202)
        self.assertEqual(sub_task_json['status'], 'DELETED')

    def test_delete_sub_task_with_token_from_another_user(self):
        user = FactoryData.create_user()
        user2 = FactoryData.create_user('user2', False)
        task = FactoryData.create_task(user)
        sub_task = FactoryData.create_sub_task(task)
        token = FactoryData.create_token(user2)
        token.generate_key()
        request = RequestFactory().delete(API_TASKS + str(task.pk) + API_SUB_TASK, HTTP_AUTHORIZATION=token.key, pk=sub_task.id)
        force_authenticate(request, user=user2, token=token)
        resp = SubTaskViewSet.as_view({'delete': 'destroy'})(request, task_pk=task.id, pk=sub_task.id)

        self.assertEqual(resp.status_code, 404)

    def test_partial_update_sub_task_without_token(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        sub_task = FactoryData.create_sub_task(task)
        data = {
            'description': 'Sub Task body message updated'
        }

        request = RequestFactory().patch(API_TASKS + str(task.pk) + API_SUB_TASK, data=data, pk=sub_task.id)

        request.user = AnonymousUser()
        resp = SubTaskViewSet.as_view({'patch': 'partial_update'})(request, task_pk=task.id, pk=sub_task.id)

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(json.loads(json.dumps(resp.data))['detail'], 'Authentication credentials were not provided.')

    def test_partial_update_sub_task_with_token(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        sub_task = FactoryData.create_sub_task(task)
        data = {
            'description': 'Sub Task body message updated'
        }

        token = FactoryData.create_token(user)
        token.generate_key()

        request = RequestFactory().patch(API_TASKS + str(task.pk) + API_SUB_TASK, data=data, pk=sub_task.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = SubTaskViewSet.as_view({'patch': 'partial_update'})(request, task_pk=task.id, pk=sub_task.id)
        task_json = json.loads(serializers.serialize('json', SubTask.objects.filter(task=task, pk=sub_task.id)))[0]['fields']

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(task_json['description'], 'Sub Task body message updated')
        self.assertEqual(json.loads(json.dumps(resp.data))['description'], 'Sub Task body message updated')
        self.assertEqual(task_json['status'], 'UPDATED')

    def test_partial_update_sub_task_with_token_from_another_user(self):
        user = FactoryData.create_user()
        user2 = FactoryData.create_user('user2', False)
        task = FactoryData.create_task(user)
        sub_task = FactoryData.create_sub_task(task)

        token = FactoryData.create_token(user2)
        token.generate_key()
        data = {
            'description': 'Sub Task body message updated'
        }

        request = RequestFactory().patch(API_TASKS + str(task.pk) + API_SUB_TASK, data=data, pk=sub_task.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = SubTaskViewSet.as_view({'patch': 'partial_update'})(request, task_pk=task.id, pk=sub_task.id)

        self.assertEqual(resp.status_code, 404)

    def test_update_bug_with_token(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        sub_task = FactoryData.create_sub_task(task)
        data = {
            'description': 'Sub Task body message updated'
        }
        token = FactoryData.create_token(user)
        token.generate_key()

        request = RequestFactory().put(API_TASKS + str(task.pk) + API_SUB_TASK, data=data, pk=sub_task.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = SubTaskViewSet.as_view({'put': 'update'})(request, task_pk=task.id, pk=sub_task.id)

        self.assertEqual(resp.status_code, 405)

    def test_options_bug_with_token(self):
        user = FactoryData.create_user()
        task = FactoryData.create_task(user)
        sub_task = FactoryData.create_sub_task(task)
        data = {
            'description': 'Sub Task body message updated'
        }
        token = FactoryData.create_token(user)
        token.generate_key()

        request = RequestFactory().options(API_TASKS + str(task.pk) + API_SUB_TASK, data=data, pk=sub_task.id, HTTP_AUTHORIZATION=token.key, content_type='application/json')
        force_authenticate(request, user=user, token=token)
        resp = SubTaskViewSet.as_view({'options': 'partial_update'})(request, task_pk=task.id, pk=sub_task.id)

        self.assertEqual(resp.status_code, 403)


