from django.shortcuts import render
import json
import requests
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import Profile
from problems.models import Problem
from .models import Plan, PlanProblem

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = ""
SITE_NAME = ""

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_plan(request):
    """Create a new learning plan based on user preferences."""
    try:
        data = json.loads(request.body.decode("utf-8"))
        name = data.get("name", "").strip()
        description = data.get("description", "").strip()
        duration_days = data.get("duration_days", 0)
        difficulty = data.get("difficulty", "").strip()
        topics = data.get("topics", [])

        if not all([name, duration_days, difficulty, topics]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            profile = Profile.objects.get(user=request.user)
            experience_level = profile.experience_level
            user_description = profile.description or "No description provided"
        except ObjectDoesNotExist:
            return JsonResponse({"error": "User profile not found. Please complete your profile setup."}, status=404)

        # Get all problems from the database
        problems = Problem.objects.all().values(
            'id', 'name', 'language', 'difficulty', 'problem_type', 'description'
        )
        problems_list = list(problems)

        # Create prompt for AI
        prompt = f"""
        You are an AI tutor helping users create personalized learning plans. Your role is to create a structured plan based on their preferences and available problems.

        **User's Experience Level:** {experience_level.capitalize()}
        **User's Background:** {user_description}

        **Plan Requirements:**
        - Name: {name}
        - Description: {description}
        - Duration: {duration_days} days
        - Difficulty Level: {difficulty}
        - Topics: {', '.join(topics)}

        **Available Problems:**
        {json.dumps(problems_list, indent=2)}

        Create a structured learning plan that:
        1. Matches the user's experience level and background
        2. Covers the requested topics
        3. Fits within the specified duration
        4. Progresses in difficulty appropriately
        5. Includes a mix of problem types

        Return a JSON array of problem IDs in the order they should be completed.
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": SITE_URL,
            "X-Title": SITE_NAME,
        }
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
        except requests.exceptions.RequestException:
            return JsonResponse({"error": "Failed to fetch response from OpenRouter"}, status=500)

        try:
            ai_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "[]")
            problem_order = json.loads(ai_response)
            
            # Create the plan
            plan = Plan.objects.create(
                user=request.user,
                name=name,
                description=description,
                duration_days=duration_days,
                difficulty=difficulty,
                topics=topics
            )

            # Add problems to the plan in the specified order
            for order, problem_id in enumerate(problem_order, start=1):
                problem = Problem.objects.get(id=problem_id)
                PlanProblem.objects.create(
                    plan=plan,
                    problem=problem,
                    order=order
                )

            return JsonResponse({
                "message": "Plan created successfully",
                "plan_id": plan.id
            })

        except (json.JSONDecodeError, IndexError, KeyError):
            return JsonResponse({"error": "Error processing AI response"}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
@login_required
def list_plans(request):
    """List all plans for the current user."""
    plans = Plan.objects.filter(user=request.user).values(
        'id', 'name', 'description', 'duration_days', 'difficulty',
        'topics', 'created_at', 'is_active'
    )
    
    plans_list = list(plans)
    
    # Add progress information for each plan
    for plan in plans_list:
        plan_problems = PlanProblem.objects.filter(plan_id=plan['id'])
        total_problems = plan_problems.count()
        completed_problems = plan_problems.filter(is_completed=True).count()
        plan['progress'] = {
            'total': total_problems,
            'completed': completed_problems,
            'percentage': (completed_problems / total_problems * 100) if total_problems > 0 else 0
        }
    
    return JsonResponse(plans_list, safe=False)

@require_http_methods(["GET"])
@login_required
def get_plan_details(request, plan_id):
    """Get detailed information about a specific plan."""
    try:
        plan = Plan.objects.get(id=plan_id, user=request.user)
        plan_problems = PlanProblem.objects.filter(plan=plan).select_related('problem').order_by('order')
        
        problems = []
        for plan_problem in plan_problems:
            problems.append({
                'id': plan_problem.problem.id,
                'name': plan_problem.problem.name,
                'language': plan_problem.problem.language,
                'difficulty': plan_problem.problem.difficulty,
                'problem_type': plan_problem.problem.problem_type,
                'order': plan_problem.order,
                'is_completed': plan_problem.is_completed,
                'completed_at': plan_problem.completed_at
            })
        
        return JsonResponse({
            'id': plan.id,
            'name': plan.name,
            'description': plan.description,
            'duration_days': plan.duration_days,
            'difficulty': plan.difficulty,
            'topics': plan.topics,
            'created_at': plan.created_at,
            'is_active': plan.is_active,
            'problems': problems
        })
    except Plan.DoesNotExist:
        return JsonResponse({"error": "Plan not found"}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_problem_status(request, plan_id, problem_id):
    """Update the completion status of a problem in a plan."""
    try:
        data = json.loads(request.body.decode("utf-8"))
        is_completed = data.get("is_completed", False)
        
        plan_problem = PlanProblem.objects.get(
            plan_id=plan_id,
            problem_id=problem_id,
            plan__user=request.user
        )
        
        plan_problem.is_completed = is_completed
        if is_completed:
            from django.utils import timezone
            plan_problem.completed_at = timezone.now()
        plan_problem.save()
        
        return JsonResponse({"message": "Problem status updated successfully"})
    except PlanProblem.DoesNotExist:
        return JsonResponse({"error": "Plan or problem not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_plan(request, plan_id):
    """Delete a plan."""
    try:
        plan = Plan.objects.get(id=plan_id, user=request.user)
        plan.delete()
        return JsonResponse({"message": "Plan deleted successfully"})
    except Plan.DoesNotExist:
        return JsonResponse({"error": "Plan not found"}, status=404)
