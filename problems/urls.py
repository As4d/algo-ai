from django.urls import path
from .views import get_problems, get_problem_details, update_status, get_question_description, get_question_boilerplate

urlpatterns = [
    path('list/', get_problems, name='get_problems'),
    path('<int:problem_id>/', get_problem_details, name='get_problem_details'),
    path('<int:problem_id>/update/', update_status, name='update_status'),
    path('<int:problem_id>/get_question_description/', get_question_description, name='get_question_description'),
    path('<int:problem_id>/get_question_boilerplate/', get_question_boilerplate, name='get_boilerplate'),
]
