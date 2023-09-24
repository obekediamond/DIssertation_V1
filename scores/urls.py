from django.urls import path
from .views import (
    provisional_score, lecturer_confirm_score, provisional_result, com_result
)


urlpatterns = [
    path('manage-score/', provisional_score, name='provisional_score'),
    path('manage-score/<int:id>/', lecturer_confirm_score, name='lecturer_confirm_score'),
    path('grade/', provisional_result, name="grade_results"),
    path('assessment/', com_result, name="ass_results"),
]
