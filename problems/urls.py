from django.urls import path
from .views import (
    get_problems, 
    get_problem_details, 
    update_progress, 
    get_question_description, 
    get_question_boilerplate,
    get_submissions
)

urlpatterns = [
    path('list/', get_problems, name='get_problems'),
    path('<int:problem_id>/', get_problem_details, name='get_problem_details'),
    path('<int:problem_id>/update/', update_progress, name='update_progress'),
    path('<int:problem_id>/description/', get_question_description, name='get_description'),
    path('<int:problem_id>/boilerplate/', get_question_boilerplate, name='get_boilerplate'),
    path('<int:problem_id>/submissions/', get_submissions, name='get_submissions'),
]
