"""qa_assessment_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework_nested.routers import SimpleRouter, NestedMixin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.views import user_view, group_view, token_view, bug_view, task_view, profile_view
from api.views.profile_view import ProfileViewSet
from api.views.sub_task_view import SubTaskViewSet

ROOT = 'api/'

router = SimpleRouter(trailing_slash=False)
router.register(r'v1/users', user_view.UserViewSet)
router.register(r'v1/groups', group_view.GroupViewSet)
router.register(r'v1/bugs', bug_view.BugViewSet)
router.register(r'v1/tasks', task_view.TaskViewSet, basename='tasks')


class NestedSimpleRouter(NestedMixin, SimpleRouter):
    pass


sub_task_router = NestedSimpleRouter(router, r'v1/tasks', lookup='task')
sub_task_router.register(r'subtasks', SubTaskViewSet, basename='task-subtasks')
profile_router = NestedSimpleRouter(router, r'v1/users', lookup='user')
profile_router.register(r'profile', ProfileViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="TODO App API",
        default_version='v1',
        description="QA-App Assessment API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(ROOT + '_manager/super', admin.site.urls),
    path(ROOT, include(router.urls)),
    path(ROOT, include(sub_task_router.urls)),
    path(ROOT, include(profile_router.urls)),
    path(ROOT + 'v1/login', token_view.TokenViewSet.login),
    re_path(ROOT + r'$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
