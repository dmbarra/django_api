from django.test import TestCase, RequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.utils import json

from api.tests.data_factory import FactoryData
from api.views.token_view import TokenViewSet

API_LOGIN = 'api/v1/login'


class TokenViewTest(TestCase):

    def test_create_token_for_exist_user(self):
        FactoryData.create_user_and_save('login_test')
        data = {
            'username': 'login_test',
            'password': 'password',
        }

        request = RequestFactory().post(API_LOGIN, data=data, content_type='application/json')
        resp = TokenViewSet.login(request)
        user_response = json.loads(json.dumps(resp.data))
        token = Token.objects.get(user=1)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user_response['token'], token.key)

    def test_create_token_without_parameters(self):
        data = {
        }

        request = RequestFactory().post(API_LOGIN, data=data, content_type='application/json')
        resp = TokenViewSet.login(request)

        self.assertEqual(resp.status_code, 400)

    def test_create_token_for_invalid_user(self):
        FactoryData.create_user_and_save('login_test')
        data = {
            'username': 'username',
            'password': 'password',
        }

        request = RequestFactory().post(API_LOGIN, data=data, content_type='application/json')
        resp = TokenViewSet.login(request)

        self.assertEqual(resp.status_code, 404)


