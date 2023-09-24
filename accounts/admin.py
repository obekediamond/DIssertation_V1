from django.contrib import admin
from .models import User, Student
from django.contrib.auth.models import Group


class UserAdmin(admin.ModelAdmin):
    # create a useradmin model for listing user records
    list_display = ['get_full_name', 'username', 'email', 'is_active', 'is_student', 'is_lecturer', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_lecturer', 'is_staff']

    class Meta:
        managed = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class ScoreAdmin(admin.ModelAdmin):
    # create a user-admin model for listing user's score
    list_display = ['student', 'course', 'assignment', 'mid_exam', 'quiz',
                    'attendance', 'final_exam', 'total', 'grade', 'comment']


# Register the admin sites
admin.site.register(User, UserAdmin)
admin.site.register(Student)
