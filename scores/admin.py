from django.contrib import admin
from django.contrib.auth.models import Group

from .models import UsersCourses, Result


class ScoreAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'course', 'assignment', 'total', 'grade', 'comment'
    ]


admin.site.register(UsersCourses, ScoreAdmin)
admin.site.register(Result)
