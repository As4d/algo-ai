from django.urls import path
from .views import (
    create_plan,
    list_plans,
    get_plan_details,
    update_problem_status,
    delete_plan
)

urlpatterns = [
    path('create/', create_plan, name='create_plan'),
    path('list/', list_plans, name='list_plans'),
    path('<int:plan_id>/', get_plan_details, name='get_plan_details'),
    path('<int:plan_id>/problems/<int:problem_id>/status/', update_problem_status, name='update_problem_status'),
    path('<int:plan_id>/delete/', delete_plan, name='delete_plan'),
] 