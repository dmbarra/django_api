from django.contrib import admin

from api.models.bug_model import Bug
from api.models.sub_task_model import SubTask
from api.models.task_model import Task
from api.models.login_info_model import LoginInfo
from api.models.profile_model import Profile

admin.site.register(Bug)
admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(LoginInfo)
admin.site.register(Profile)
