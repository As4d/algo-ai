from django.shortcuts import render
import json
import requests
import os
import html
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import Profile
from problems.models import Problem
from .models import Plan, PlanProblem
import traceback
import logging

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = ""
SITE_NAME = ""

# At the top after imports
logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_plan(request):
    """
    Create a new learning plan based on user preferences.
    
    Args:
        request (HttpRequest): The HTTP request object containing:
            - name (str): Name of the plan
            - description (str): Description of the plan
            - duration_days (int): Duration of the plan in days
            - difficulty (str): Difficulty level of the plan
            - problem_types (list): List of problem types to cover
            
    Returns:
        JsonResponse: A JSON response containing:
            - On success:
                - message (str): Success message
                - plan_id (int): ID of the created plan
                - explanation (str): AI's explanation of the plan
            - On error:
                - error (str): Error message
                - reason (str, optional): Additional error details
    """
    try:
        logger.info("Starting create_plan function")
        data = json.loads(request.body.decode("utf-8"))
        logger.info(f"Request data: {data}")
        
        # Get user inputs
        name = data.get("name", "").strip()
        description = data.get("description", "").strip()
        duration_days = int(data.get("duration_days", 0))  # Convert to int for safety
        difficulty = data.get("difficulty", "").strip()
        problem_types = data.get("problem_types", [])  # Changed from topics to problem_types
        
        logger.info(f"Plan parameters: name={name}, duration={duration_days}, difficulty={difficulty}, problem_types={problem_types}")

        if not all([name, duration_days, difficulty, problem_types]):
            logger.warning("Missing required fields in request")
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            logger.info("Fetching user profile")
            profile = Profile.objects.get(user=request.user)
            experience_level = profile.experience_level
            user_description = profile.description or "No description provided"
            logger.info(f"User profile: experience={experience_level}, description={user_description}")
        except ObjectDoesNotExist:
            logger.error("User profile not found")
            return JsonResponse({"error": "User profile not found. Please complete your profile setup."}, status=404)

        # Get problems from the database filtered by problem types
        logger.info(f"Fetching problems from database for types: {problem_types}")
        problems = Problem.objects.filter(problem_type__in=problem_types).values(
            'id', 'name', 'language', 'difficulty', 'problem_type', 'description'
        )
        problems_list = list(problems)
        logger.info(f"Found {len(problems_list)} problems for selected types")

        if not problems_list:
            logger.warning(f"No problems found for types: {problem_types}")
            return JsonResponse({
                "error": "No problems available",
                "reason": f"No problems found for the selected problem types: {', '.join(problem_types)}"
            }, status=400)

        # Create prompt for AI
        logger.info("Creating AI prompt")
        prompt = f"""
        You are an AI tutor helping users create personalized learning plans. Your role is to create a structured plan based on their preferences and available problems.

        **User's Experience Level:** {experience_level.capitalize()}
        **User's Background:** {user_description}

        **Plan Requirements:**
        - Name: {name}
        - Description: {description}
        - Duration: {duration_days} days
        - Target Difficulty Level: {difficulty} (This is a general guideline - you can include a mix of problems with different difficulties)
        - Problem Types: {', '.join(problem_types)}

        **Available Problems:**
        {json.dumps(problems_list, indent=2)}

        Create a structured learning plan that:
        1. Matches the user's experience level and background
        2. Uses a mix of the selected problem types
        3. Fits within the specified duration
        4. Aims for an AVERAGE difficulty of {difficulty}, but can include:
           - For 'beginner' plans: mostly easy problems with some intermediate ones
           - For 'intermediate' plans: a mix of easy, intermediate, and some hard problems
           - For 'advanced' plans: mostly hard problems with some intermediate ones
        5. ONLY uses problems from the selected types: {', '.join(problem_types)}

        IMPORTANT: You MUST respond in the following format:
        1. First, provide a brief explanation of your plan.
        2. Then on a new line, provide ONLY a JSON array of problem IDs like this: [1, 2, 3]
        3. Do not include any other text or formatting after the JSON array.

        Example response format:
        I've created a plan that combines problems from your selected types ({', '.join(problem_types)}), with an average difficulty suitable for {difficulty} level learners. The problems progress in difficulty and are spread over {duration_days} days.

        [1, 5, 8, 12, 15]

        If you cannot create a suitable plan with the available problems, respond with:
        I cannot create a suitable plan because [reason].

        []
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": SITE_URL,
            "X-Title": SITE_NAME,
        }
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [{"role": "user", "content": prompt}]
        }

        logger.info("Sending request to OpenRouter API")
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            logger.info("Received response from OpenRouter API")
            logger.debug(f"OpenRouter API response: {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch response from OpenRouter: {str(e)}")
            return JsonResponse({"error": "Failed to fetch response from OpenRouter"}, status=500)

        try:
            response_json = response.json()
            logger.debug(f"API response JSON: {response_json}")
            
            ai_response = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.info(f"AI response content: {ai_response}")
            
            # Extract explanation and problem_order from AI response
            # Split the response at the last newline to separate explanation from JSON array
            parts = ai_response.rsplit('\n', 1)
            if len(parts) == 2:
                explanation = parts[0].strip()
                problem_order_str = parts[1].strip()
            else:
                explanation = ai_response
                problem_order_str = "[]"

            logger.info(f"Extracted explanation: {explanation}")
            logger.info(f"Extracted problem_order_str: {problem_order_str}")
            
            try:
                # Clean up the problem_order_str to ensure it's valid JSON
                problem_order_str = problem_order_str.strip('`').strip()
                if not problem_order_str.startswith('['):
                    # Try to find array in the string
                    import re
                    match = re.search(r'\[(.*?)\]', problem_order_str)
                    if match:
                        problem_order_str = match.group(0)
                    else:
                        problem_order_str = "[]"

                problem_order = json.loads(problem_order_str)
                logger.info(f"Parsed problem_order: {problem_order}")
                
                if not problem_order:
                    logger.warning("Empty problem_order, plan creation not possible")
                    return JsonResponse({
                        "error": "Could not create plan",
                        "reason": "The AI was unable to generate a suitable problem sequence. Please try again with different parameters.",
                        "explanation": explanation
                    }, status=400)
                
                # Verify all problems exist and are of correct type
                valid_problems = []
                for problem_id in problem_order:
                    try:
                        problem = Problem.objects.get(id=problem_id, problem_type__in=problem_types)
                        valid_problems.append(problem_id)
                    except Problem.DoesNotExist:
                        logger.warning(f"Problem {problem_id} not found or wrong type")
                        continue

                if not valid_problems:
                    logger.error("No valid problems found")
                    return JsonResponse({
                        "error": "Could not create plan",
                        "reason": "None of the suggested problems are available. Please try again."
                    }, status=400)

                # Create the plan
                logger.info("Creating plan in database")
                plan = Plan.objects.create(
                    user=request.user,
                    name=name,
                    description=description,
                    duration_days=duration_days,
                    difficulty=difficulty,
                    problem_types=problem_types,
                    ai_explanation=explanation
                )
                logger.info(f"Created plan with ID: {plan.id}")

                # Add problems to the plan in the specified order
                logger.info("Adding problems to plan")
                for order, problem_id in enumerate(valid_problems, start=1):
                    problem = Problem.objects.get(id=problem_id)
                    PlanProblem.objects.create(
                        plan=plan,
                        problem=problem,
                        order=order
                    )
                    logger.info(f"Added problem {problem_id} to plan with order {order}")

                return JsonResponse({
                    "message": "Plan created successfully",
                    "plan_id": plan.id,
                    "explanation": explanation
                })

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for problem_order: {str(e)}")
                return JsonResponse({
                    "error": "Error parsing problem list from AI response",
                    "reason": "The AI response was not in the expected format. Please try again."
                }, status=400)

        except (json.JSONDecodeError, IndexError, KeyError) as e:
            logger.error(f"Error processing AI response: {str(e)}")
            logger.error(f"Response content: {response.text}")
            return JsonResponse({"error": "Error processing AI response"}, status=500)

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in create_plan: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
@login_required
def list_plans(request):
    """
    List all plans for the current user.
    
    Args:
        request (HttpRequest): The HTTP request object containing the authenticated user.
        
    Returns:
        JsonResponse: A JSON response containing a list of plans, where each plan contains:
            - id (int): Plan ID
            - name (str): Plan name
            - description (str): Plan description
            - duration_days (int): Plan duration in days
            - difficulty (str): Plan difficulty level
            - topics (list): List of topics
            - created_at (datetime): Creation timestamp
            - is_active (bool): Whether the plan is active
            - progress (dict): Progress information containing:
                - total (int): Total number of problems
                - completed (int): Number of completed problems
                - percentage (float): Completion percentage
            - is_completed (bool): Whether all problems are completed
    """
    plans = Plan.objects.filter(user=request.user).values(
        'id', 'name', 'description', 'duration_days', 'difficulty',
        'problem_types', 'created_at', 'is_active'
    )
    
    plans_list = list(plans)
    
    # Add progress information for each plan
    for plan in plans_list:
        plan_problems = PlanProblem.objects.filter(plan_id=plan['id'])
        total_problems = plan_problems.count()
        completed_problems = plan_problems.filter(is_completed=True).count()
        
        percentage = (completed_problems / total_problems * 100) if total_problems > 0 else 0
        plan['progress'] = {
            'total': total_problems,
            'completed': completed_problems,
            'percentage': round(percentage, 2)
        }
        
        # Add 'completed' flag if all problems are completed
        plan['is_completed'] = (completed_problems == total_problems) and total_problems > 0
    
    return JsonResponse(plans_list, safe=False)

@require_http_methods(["GET"])
@login_required
def get_plan_details(request, plan_id):
    """
    Get detailed information about a specific plan.
    
    Args:
        request (HttpRequest): The HTTP request object containing the authenticated user.
        plan_id (int): The ID of the plan to retrieve details for.
        
    Returns:
        JsonResponse: A JSON response containing:
            - On success:
                - id (int): Plan ID
                - name (str): Plan name
                - description (str): Plan description
                - duration_days (int): Plan duration in days
                - difficulty (str): Plan difficulty level
                - topics (list): List of topics
                - created_at (datetime): Creation timestamp
                - is_active (bool): Whether the plan is active
                - problems (list): List of problems in the plan
                - progress (dict): Progress information
                - ai_explanation (str): AI's explanation of the plan
                - is_completed (bool): Whether all problems are completed
            - On error:
                - error (str): Error message
    """
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
        
        # Count completed problems for progress calculation
        total_problems = len(problems)
        completed_problems = sum(1 for p in problems if p['is_completed'])
        percentage = (completed_problems / total_problems * 100) if total_problems > 0 else 0
        
        return JsonResponse({
            'id': plan.id,
            'name': plan.name,
            'description': plan.description,
            'duration_days': plan.duration_days,
            'difficulty': plan.difficulty,
            'problem_types': plan.problem_types,
            'created_at': plan.created_at,
            'is_active': plan.is_active,
            'problems': problems,
            'progress': {
                'total': total_problems,
                'completed': completed_problems,
                'percentage': round(percentage, 2)
            },
            'ai_explanation': plan.ai_explanation,
            'is_completed': (completed_problems == total_problems) and total_problems > 0
        })
    except Plan.DoesNotExist:
        return JsonResponse({"error": "Plan not found"}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_problem_status(request, plan_id, problem_id):
    """
    Update the completion status of a problem in a plan.
    
    Args:
        request (HttpRequest): The HTTP request object containing:
            - is_completed (bool): New completion status
        plan_id (int): The ID of the plan
        problem_id (int): The ID of the problem to update
        
    Returns:
        JsonResponse: A JSON response containing:
            - On success:
                - message (str): Success message
            - On error:
                - error (str): Error message
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        is_completed = bool(data.get("is_completed", False))  # Convert to bool for safety
        
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
    """
    Delete a plan.
    
    Args:
        request (HttpRequest): The HTTP request object containing the authenticated user.
        plan_id (int): The ID of the plan to delete.
        
    Returns:
        JsonResponse: A JSON response containing:
            - On success:
                - message (str): Success message
            - On error:
                - error (str): Error message
    """
    try:
        plan = Plan.objects.get(id=plan_id, user=request.user)
        plan.delete()
        return JsonResponse({"message": "Plan deleted successfully"})
    except Plan.DoesNotExist:
        return JsonResponse({"error": "Plan not found"}, status=404)
