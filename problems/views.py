from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

from .models import Problem, UserProgress, Submission

@require_http_methods(["GET"])
def get_problems(request):
    """
    Returns a list of all problems with their metadata.
    Optional query parameter 'type' to filter by problem type.
    """
    problem_type = request.GET.get('type', 'problem_set')
    problems = Problem.objects.filter(problem_type=problem_type).values(
        'id', 'name', 'language', 'difficulty', 'problem_type', 'order'
    )
    return JsonResponse(list(problems), safe=False)

@require_http_methods(["GET"])
@login_required
def get_problem_details(request, problem_id):
    """
    Returns full details of a specific problem, including markdown description and test cases.
    """
    problem = get_object_or_404(Problem, id=problem_id)
    user_progress, _ = UserProgress.objects.get_or_create(
        user=request.user, 
        problem=problem,
        defaults={
            'is_completed': False,
            'time_spent': 0,
            'attempts': 0
        }
    )

    return JsonResponse({
        "name": problem.name,
        "language": problem.language,
        "difficulty": problem.difficulty,
        "problem_type": problem.problem_type,
        "description": problem.description,
        "test_cases": problem.test_cases,
        "is_completed": user_progress.is_completed,
        "time_spent": user_progress.time_spent,
        "attempts": user_progress.attempts,
        "order": problem.order
    })

@require_http_methods(["POST"])
@login_required
def update_progress(request, problem_id):
    """
    Updates user progress on a problem.
    """
    data = json.loads(request.body.decode('utf-8'))
    is_completed = data.get("is_completed", False)
    time_spent = data.get("time_spent", 0)
    code = data.get("code", "")
    language = data.get("language", "")

    problem = get_object_or_404(Problem, id=problem_id)
    user_progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        problem=problem,
        defaults={
            'is_completed': False,
            'time_spent': 0,
            'attempts': 0
        }
    )

    # Update progress
    if not created:
        user_progress.attempts += 1
        if time_spent > 0:
            user_progress.time_spent = time_spent
        user_progress.is_completed = is_completed
        user_progress.save()

    # Create submission record
    submission = Submission.objects.create(
        user=request.user,
        problem=problem,
        code_submitted=code,
        status='completed' if is_completed else 'attempted',
        language=language
    )

    return JsonResponse({
        "message": "Progress updated successfully",
        "submission_id": submission.id
    })

@require_http_methods(["GET"])
def get_question_description(request, problem_id):
    """
    Returns the description of a specific problem.
    """
    problem = get_object_or_404(Problem, id=problem_id)
    return JsonResponse({"description": problem.description})

@require_http_methods(["GET"])
def get_question_boilerplate(request, problem_id):
    """
    Returns the boilerplate code for a specific problem.
    """
    problem = get_object_or_404(Problem, id=problem_id)
    return JsonResponse({"boilerplate": problem.boilerplate_code})

@require_http_methods(["GET"])
@login_required
def get_submissions(request, problem_id):
    """
    Returns all submissions for a specific problem by the current user.
    """
    submissions = Submission.objects.filter(
        user=request.user,
        problem_id=problem_id
    ).values('id', 'status', 'language', 'created_at', 'code_submitted')
    return JsonResponse(list(submissions), safe=False)