from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate
from rest_framework.utils import json

from api.views.token_view import TokenViewSet


class TokenViewTest(TestCase):

    def test_create_token_for_exist_user(self):
        self.create_user('login_test')
        data = {
            'username': 'login_test',
            'password': 'password',
        }

        request = RequestFactory().post('v1/api/login', data=data, content_type='application/json')
        resp = TokenViewSet.login(request)
        user_response = json.loads(json.dumps(resp.data))
        token = Token.objects.get(user=1)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['token'], token.key)

    def test_create_token_without_parameters(self):
        data = {
        }

        request = RequestFactory().post('v1/api/login', data=data, content_type='application/json')
        resp = TokenViewSet.login(request)

        self.assertEqual(resp.status_code, 400)

    def test_create_token_for_invalid_user(self):
        self.create_user('login_test')
        data = {
            'username': 'username',
            'password': 'password',
        }

        request = RequestFactory().post('v1/api/login', data=data, content_type='application/json')
        resp = TokenViewSet.login(request)

        self.assertEqual(resp.status_code, 404)

    @staticmethod
    def create_user(user='username', root=False):
        user = User.objects.create(username=user, password='password', email='email', is_superuser=root)
        user.set_password('password')
        user.save()

    @staticmethod
    def create_token(user):
        return Token.objects.create(user=user)
