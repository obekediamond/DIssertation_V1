from django.urls import path
from .views import *

urlpatterns = [
    path('', LookupView.as_view(), name='query'),
    path('lookup/view', LookupPost.as_view(), name='query'),
]
