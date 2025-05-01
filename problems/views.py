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
    
    Args:
        request (HttpRequest): The HTTP request object containing:
            - type (str, optional): Problem type to filter by (default: 'problem_set')
            
    Returns:
        JsonResponse: A JSON response containing a list of problems, where each problem contains:
            - id (int): Problem ID
            - name (str): Problem name
            - language (str): Programming language
            - difficulty (str): Problem difficulty level
            - problem_type (str): Type of problem
            - order (int): Problem order
            - status (str): Problem status ('completed', 'started', or 'not_started')
    """
    problem_type = request.GET.get('type', 'problem_set')
    problems = Problem.objects.filter(problem_type=problem_type).values(
        'id', 'name', 'language', 'difficulty', 'problem_type', 'order'
    )
    
    # Convert to list for modification
    problems_list = list(problems)
    
    # If user is authenticated, include their progress
    if request.user.is_authenticated:
        progress_dict = {
            progress.problem_id: {
                'is_completed': progress.is_completed,
                'attempts': progress.attempts
            }
            for progress in UserProgress.objects.filter(
                user=request.user,
                problem_id__in=[p['id'] for p in problems]
            )
        }
        
        # Add status to each problem
        for problem in problems_list:
            progress = progress_dict.get(problem['id'], {})
            if progress.get('is_completed'):
                problem['status'] = 'completed'
            elif progress.get('attempts', 0) > 0:
                problem['status'] = 'started'
            else:
                problem['status'] = 'not_started'
    else:
        # For unauthenticated users, set all problems as not started
        for problem in problems_list:
            problem['status'] = 'not_started'
    
    return JsonResponse(problems_list, safe=False)

@require_http_methods(["GET"])
@login_required
def get_problem_details(request, problem_id):
    """
    Returns full details of a specific problem, including markdown description and test cases.
    
    Args:
        request (HttpRequest): The HTTP request object containing the authenticated user.
        problem_id (int): The ID of the problem to retrieve details for.
        
    Returns:
        JsonResponse: A JSON response containing:
            - name (str): Problem name
            - language (str): Programming language
            - difficulty (str): Problem difficulty level
            - problem_type (str): Type of problem
            - description (str): Problem description in markdown
            - test_cases (list): List of test cases
            - is_completed (bool): Whether the user has completed the problem
            - time_spent (int): Time spent on the problem in seconds
            - attempts (int): Number of attempts made
            - order (int): Problem order
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
    
    Args:
        request (HttpRequest): The HTTP request object containing:
            - is_completed (bool): Whether the problem was completed
            - time_spent (int): Time spent on the problem in seconds
            - code (str): Code submitted by the user
            - language (str): Programming language used
        problem_id (int): The ID of the problem to update progress for.
        
    Returns:
        JsonResponse: A JSON response containing:
            - message (str): Success message
            - submission_id (int): ID of the created submission record
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
    
    Args:
        request (HttpRequest): The HTTP request object.
        problem_id (int): The ID of the problem to get the description for.
        
    Returns:
        JsonResponse: A JSON response containing:
            - description (str): Problem description in markdown
    """
    problem = get_object_or_404(Problem, id=problem_id)
    return JsonResponse({"description": problem.description})

@require_http_methods(["GET"])
def get_question_boilerplate(request, problem_id):
    """
    Returns the boilerplate code for a specific problem.
    
    Args:
        request (HttpRequest): The HTTP request object.
        problem_id (int): The ID of the problem to get the boilerplate for.
        
    Returns:
        JsonResponse: A JSON response containing:
            - boilerplate (str): Boilerplate code for the problem
    """
    problem = get_object_or_404(Problem, id=problem_id)
    return JsonResponse({"boilerplate": problem.boilerplate_code})

@require_http_methods(["GET"])
@login_required
def get_submissions(request, problem_id):
    """
    Returns all submissions for a specific problem by the current user.
    
    Args:
        request (HttpRequest): The HTTP request object containing the authenticated user.
        problem_id (int): The ID of the problem to get submissions for.
        
    Returns:
        JsonResponse: A JSON response containing a list of submissions, where each submission contains:
            - id (int): Submission ID
            - status (str): Submission status ('completed' or 'attempted')
            - language (str): Programming language used
            - created_at (datetime): Submission timestamp
            - code_submitted (str): Submitted code
    """
    submissions = Submission.objects.filter(
        user=request.user,
        problem_id=problem_id
    ).values('id', 'status', 'language', 'created_at', 'code_submitted')
    return JsonResponse(list(submissions), safe=False)

@require_http_methods(["GET"])
def get_problem_types(request):
    """
    Returns a list of unique problem types from the database.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        JsonResponse: A JSON response containing a list of unique problem types (str)
    """
    problem_types = Problem.objects.values_list('problem_type', flat=True).distinct()
    return JsonResponse(list(problem_types), safe=False)

@login_required
def get_last_submission(request, problem_id):
    """
    Get the last submission for a specific problem by the current user.
    
    Args:
        request (HttpRequest): The HTTP request object containing the authenticated user.
        problem_id (int): The ID of the problem to get the last submission for.
        
    Returns:
        JsonResponse: A JSON response containing:
            - id (int): Submission ID
            - status (str): Submission status ('completed' or 'attempted')
            - language (str): Programming language used
            - created_at (datetime): Submission timestamp
            - code_submitted (str): Submitted code
    """
    submission = Submission.objects.filter(
        user=request.user,
        problem_id=problem_id
    ).order_by('-created_at').first()
    
    if submission:
        return JsonResponse({
            'id': submission.id,
            'status': submission.status,
            'language': submission.language,
            'created_at': submission.created_at,
            'code_submitted': submission.code_submitted
        })
    else:
        return JsonResponse({'error': 'No submission found'}, status=404)