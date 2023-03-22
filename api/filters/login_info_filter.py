import django_filters
from api.models.login_info_model import LoginInfo


class LoginInfoFilter(django_filters.FilterSet):
    class Meta:
        model = LoginInfo
        fields = ['user', 'timestamp']
