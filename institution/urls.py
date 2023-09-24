from django.urls import path

from .views import (index_view, add_post, edit_post, delete_post, session_list_view, session_add_view,
                    session_update_view, session_delete_view, trimester_list_view, trimester_add_view,
                    trimester_update_view, trimester_delete_view, dashboard_view)

urlpatterns = [
    path('', index_view, name='home'),
    path('add_item/', add_post, name='add_item'),
    path('item/<int:pk>/edit/', edit_post, name='edit_post'),
    path('item/<int:pk>/delete/', delete_post, name='delete_post'),
    path('session/', session_list_view, name="session_list"),
    path('session/add/', session_add_view, name="add_session"),
    path('session/<int:pk>/edit/', session_update_view, name="edit_session"),
    path('session/<int:pk>/delete/', session_delete_view, name="delete_session"),
    path('trimester/', trimester_list_view, name="trimester_list"),
    path('trimester/add/', trimester_add_view, name="add_trimester"),
    path('trimester/<int:pk>/edit/', trimester_update_view, name="edit_trimester"),
    path('trimester/<int:pk>/delete/', trimester_delete_view, name="delete_trimester"),
    path('dashboard/', dashboard_view, name="dashboard"),
]
