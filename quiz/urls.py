from django.urls import path
from .views import *

urlpatterns = [

    path('<slug>/quizzes/', quiz_list, name='quiz_index'),
    path('progress/', view=QuizUserProgressView.as_view(), name='quiz_progress'),
    path('marking_list/', view=QuizMarkingList.as_view(), name='quiz_marking'),
    path('marking/<int:pk>/', view=QuizMarkingDetail.as_view(), name='quiz_marking_detail'),
    path('<int:pk>/<slug>/take/', view=QuizTake.as_view(), name='quiz_take'),
    path('<slug>/quiz_add/', QuizCreateView.as_view(), name='quiz_create'),
    path('<slug>/quiz_addition/', QuizCreateViewEssay.as_view(), name='quiz_create_essay'),
    path('<slug>/<int:pk>/add/', QuizUpdateView.as_view(), name='quiz_update'),
    path('<slug>/<int:pk>/delete/', quiz_delete, name='quiz_delete'),
    path('mc-question/add/<slug>/<int:quiz_id>/', MCQuestionCreate.as_view(), name='mc_create'),
    path('<slug>/essay_create/<int:quiz_id>/', EssayQuestionCreate.as_view(), name='essay_create'),
    path('<int:pk>/<slug:slug>/execute_code/', CodeExecutionView.as_view(), name='execute_code'),
    path('<int:course_pk>/<slug:quiz_slug>/quiz_completion/', quiz_completion, name='quiz_completion'),

]
