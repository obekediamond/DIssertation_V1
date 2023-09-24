from django.urls import path
from .views import *


urlpatterns = [

    path('', view_program, name='programs'),
    path('<int:pk>/detail/', program_detail, name='program_detail'),
    path('add/', add_program, name='add_program'),
    path('<int:pk>/edit/', edit_program, name='edit_program'),
    path('<int:pk>/delete/', delete_program, name='delete_program'),
    path('course/<slug>/detail/', course_view, name='course_detail'),
    path('<int:pk>/course/add/', add_course, name='add_course'),
    path('course/<slug>/edit/', edit_course, name='edit_course'),
    path('course/delete/<slug>/', delete_course, name='delete_course'),
    path('course/<slug>/documentations/upload/', handle_file_upload, name='upload_file_view'),
    path('course/<slug>/documentations/<int:file_id>/edit/', handle_file_edit, name='upload_file_edit'),
    path('course/<slug>/documentations/<int:file_id>/delete/', handle_file_delete, name='upload_file_delete'),
    path('course/<slug>/video_tutorials/upload/', handle_video_upload, name='upload_video'),
    path('course/<slug>/video_tutorials/<video_slug>/detail/', handle_video_single, name='video_single'),
    path('course/<slug>/video_tutorials/<video_slug>/edit/', handle_video_edit, name='upload_video_edit'),
    path('course/<slug>/video_tutorials/<video_slug>/delete/', handle_video_delete, name='upload_video_delete'),
    path('course/assign/', allocate_course.as_view(), name='course_allocation'),
    path('course/allocated/', view_allocated_course, name='view_allocated_course'),
    path('allocated_course/<int:pk>/edit/', edit_allocated_course, name='edit_allocated_course'),
    path('course/<int:pk>/deallocate/', deallocate_course, name='course_deallocate'),
    path('course/registration/', student_add_course, name='student_add_course'),
    path('course/drop/', student_drop_course, name='student_drop_course'),
    path('my_courses/', user_course_list, name="user_course_list"),
]
