from django.urls import path, include
from .views import (profile, profile_from_admin, admin_panel, update_profile, password_change, LecturerListView,
                    StudentListView, lecturer_add_view, edit_lecturer, delete_lecturer, student_add_view, edit_student,
                    delete_student, validate_user, register)

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('profile/', profile, name='profile'),
    path('profile/<int:id>/detail/', profile_from_admin, name='profile_from_admin'),
    path('setting/', update_profile, name='edit_profile'),
    path('password_change/', password_change, name='password_change'),
    path('lecturers/', LecturerListView.as_view(), name='lecturer_list'),
    path('lecturer/add/', lecturer_add_view, name='add_lecturer'),
    path('staff/<int:pk>/edit/', edit_lecturer, name='staff_edit'),
    path('lecturers/<int:pk>/delete/', delete_lecturer, name='lecturer_delete'),
    path('students/', StudentListView.as_view(), name='student_list'),
    path('student/add/', student_add_view, name='add_student'),
    path('student/<int:pk>/edit/', edit_student, name='student_edit'),
    path('students/<int:pk>/delete/', delete_student, name='student_delete'),
    path('ajax/validate-username/', validate_user, name='validate_user'),
    path('register/', register, name='register'),

]
