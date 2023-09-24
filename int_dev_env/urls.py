from django.urls import path
from .views import *

app_name = 'int_dev_env'

urlpatterns = [
    path('execute-code/', execute_code, name='execute_code'),

]
