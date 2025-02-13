from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

from .models import Problem, UserProgress

@require_http_methods(["GET"])
def get_problems(request):
    """
    Returns a list of all problems with their metadata.
    """
    problems = Problem.objects.all().values('id', 'name', 'language', 'difficulty')
    return JsonResponse(list(problems), safe=False)

@require_http_methods(["GET"])
@login_required
def get_problem_details(request, problem_id):
    """
    Returns full details of a specific problem, including markdown description and test cases.
    """
    problem = get_object_or_404(Problem, id=problem_id)
    user_progress, _ = UserProgress.objects.get_or_create(user=request.user, problem=problem)

    return JsonResponse({
        "name": problem.name,
        "language": problem.language,
        "difficulty": problem.difficulty,
        "description": problem.get_markdown_description(),
        "test_cases": problem.test_cases,
        "status": user_progress.status,
        "completion_time": user_progress.completion_time
    })

@require_http_methods(["POST"])
@login_required
def update_status(request, problem_id):
    """
    Updates user progress on a problem.
    """
    data = json.loads(request.body.decode('utf-8'))
    status = data.get("status")
    completion_time = data.get("completion_time", None)

    if status not in ["started", "completed"]:
        return JsonResponse({"error": "Invalid status"}, status=400)

    problem = get_object_or_404(Problem, id=problem_id)
    user_progress, _ = UserProgress.objects.get_or_create(user=request.user, problem=problem)
    user_progress.status = status

    if status == "completed" and completion_time is not None:
        user_progress.completion_time = completion_time

    user_progress.save()
    return JsonResponse({"message": "Status updated successfully"})
