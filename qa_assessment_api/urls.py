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
from django.urls import include, path
from rest_framework import routers
from api.views import user_view, group_view, token_view, bug_view

router = routers.DefaultRouter()
router.register(r'api/users', user_view.UserViewSet)
router.register(r'api/groups', group_view.GroupViewSet)
router.register(r'api/bugs', bug_view.BugViewSet)

urlpatterns = [
    path('_manager/super', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/login', token_view.TokenViewSet.login),
]
