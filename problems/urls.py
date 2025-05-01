from django.urls import path
from .views import (
    get_problems, 
    get_problem_details, 
    update_progress, 
    get_question_description, 
    get_question_boilerplate,
    get_submissions,
    get_problem_types,
    get_last_submission
)

urlpatterns = [
    path('list/', get_problems, name='get_problems'),
    path('types/', get_problem_types, name='get_problem_types'),
    path('<int:problem_id>/', get_problem_details, name='get_problem_details'),
    path('<int:problem_id>/update/', update_progress, name='update_progress'),
    path('<int:problem_id>/description/', get_question_description, name='get_description'),
    path('<int:problem_id>/boilerplate/', get_question_boilerplate, name='get_boilerplate'),
    path('<int:problem_id>/submissions/', get_submissions, name='get_submissions'),
    path('<int:problem_id>/last_submission/', get_last_submission, name='last_submission'),
]
