"""
Code execution module for handling user code submissions and testing.

This module provides functionality to:
- Execute user code in a safe environment
- Run test cases against submitted code
- Update user progress and gamification elements
- Handle code submissions and testing endpoints
"""

import io
import sys
import traceback
import json
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from problems.models import Problem, UserProgress, Submission
from gamification.models import LeaderboardEntry
from accounts.models import Profile

# Constants
CODE_EXECUTION_TIMEOUT = 10  # seconds

# Dictionary of allowed built-in functions for code execution
SAFE_FUNCTIONS = {
    "print": print,
    "len": len,
    "range": range,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "enumerate": enumerate,
    "sum": sum,
    "min": min,
    "max": max,
    "sorted": sorted,
    "abs": abs,
    "all": all,
    "any": any,
    "round": round,
    "__builtins__": None,  # Restrict access to other builtins
}

def create_execution_environment(test_input=""):
    """
    Creates a safe execution environment with allowed functions and input handling.
    
    Args:
        test_input (str): Comma-separated input values for testing.
        
    Returns:
        dict: Environment dictionary with safe functions and input handling.
    """
    env = SAFE_FUNCTIONS.copy()
    
    if test_input:
        input_values = [x.strip() for x in test_input.split(',')]
        input_queue = iter(input_values)
        
        def custom_input(prompt=""):
            try:
                return next(input_queue)
            except StopIteration:
                return ""
        
        env["input"] = custom_input
    
    return env

def run_code_with_test(code, test_input=""):
    """
    Runs user code in a safe environment with timeout protection.
    
    Args:
        code (str): Python code to execute.
        test_input (str): Comma-separated input values for testing.
        
    Returns:
        dict: Execution result containing success status and output/error.
    """
    output_buffer = io.StringIO()
    sys.stdout = output_buffer
    sys.stderr = output_buffer
    
    result = None
    
    def target():
        nonlocal result
        try:
            # Create safe execution environment
            globals_dict = create_execution_environment(test_input)
            
            # Execute the code
            exec(code, globals_dict)
            
            output = output_buffer.getvalue()
            result = {"success": True, "output": output.strip()}
        except Exception as e:
            result = {"success": False, "error": traceback.format_exc()}
        finally:
            # Restore system streams
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            if test_input:
                sys.stdin = sys.__stdin__
    
    # Run code in thread with timeout
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout=CODE_EXECUTION_TIMEOUT)
    
    if thread.is_alive():
        return {
            "success": False,
            "error": f"Code execution timed out after {CODE_EXECUTION_TIMEOUT} seconds"
        }
    
    return result if result is not None else {
        "success": False,
        "error": "Unknown error occurred"
    }

def compare_outputs(expected, actual):
    """
    Compare expected and actual outputs, ignoring whitespace differences.
    
    Args:
        expected (str): Expected output from test case.
        actual (str): Actual output from code execution.
    
    Returns:
        bool: True if outputs match after normalization.
    """
    expected = expected.strip().replace('\r\n', '\n')
    actual = actual.strip().replace('\r\n', '\n')
    return expected == actual

def update_leaderboard(user, problem, was_completed_before):
    """
    Update the leaderboard for a user when they complete a problem.
    
    Args:
        user: User object for the current user.
        problem: Problem object that was attempted.
        was_completed_before (bool): Whether the user had previously completed this problem.
    
    Returns:
        LeaderboardEntry: Updated or created leaderboard entry.
    """
    leaderboard_entry, created = LeaderboardEntry.objects.get_or_create(
        user=user,
        defaults={'total_solved': 1}
    )
    
    if not created and not was_completed_before:
        leaderboard_entry.total_solved += 1
        leaderboard_entry.save()
    
    return leaderboard_entry

def update_user_progress(user, problem, time_spent, all_tests_passed):
    """
    Update the user's progress for a specific problem.
    
    Args:
        user: User object for the current user.
        problem: Problem object that was attempted.
        time_spent (int): Time spent on the problem in seconds.
        all_tests_passed (bool): Whether all test cases passed.
    
    Returns:
        UserProgress: Updated or created progress entry.
    """
    user_progress, created = UserProgress.objects.get_or_create(
        user=user,
        problem=problem,
        defaults={
            'is_completed': False,
            'time_spent': 0,
            'attempts': 0
        }
    )

    user_progress.attempts += 1
    if time_spent > 0:
        user_progress.time_spent = time_spent
    if all_tests_passed:
        user_progress.is_completed = True
        user_progress.last_submitted = timezone.now()
    user_progress.save()
    
    return user_progress

def create_submission(user, problem, user_code, all_tests_passed):
    """
    Create a submission record for a user's code attempt.
    
    Args:
        user: User object for the current user.
        problem: Problem object that was attempted.
        user_code (str): The code submitted by the user.
        all_tests_passed (bool): Whether all test cases passed.
    
    Returns:
        Submission: Created submission record.
    """
    return Submission.objects.create(
        user=user,
        problem=problem,
        code_submitted=user_code,
        status='completed' if all_tests_passed else 'attempted',
        language=problem.language,
        created_at=timezone.now()
    )

def update_streak(user):
    """
    Update the user's problem-solving streak.
    
    Args:
        user: User object for the current user.
    
    Notes:
        - Streak increases by 1 per day when a problem is solved
        - Resets if more than 1 day passes between solutions
        - Updates high score streak if current streak is higher
    """
    today = timezone.now().date()
    profile = Profile.objects.get(user=user)
    
    if profile.last_solved_date is None or (today - profile.last_solved_date).days > 1:
        profile.streak = 1
    elif profile.last_solved_date < today:
        profile.streak += 1
        
    if profile.streak > profile.high_score_streak:
        profile.high_score_streak = profile.streak
        
    profile.last_solved_date = today
    profile.save()

@csrf_exempt
def execute_code(request):
    """
    View function to handle code execution requests.
    
    Handles both simple code execution and test case validation.
    Updates user progress, leaderboard, and streaks on successful test completion.
    
    Args:
        request: HTTP request object containing code and test parameters.
    
    Returns:
        JsonResponse: Execution results or error message.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        user_code = data.get("code", "").strip()
        problem_id = data.get("problem_id")
        run_tests = data.get("run_tests", False)
        time_spent = data.get("time_spent", 0)

        if not user_code:
            return JsonResponse({"error": "No code provided"}, status=400)

        # Simple code execution without tests
        if not run_tests:
            result = run_code_with_test(user_code)
            if result["success"]:
                return JsonResponse({"output": result["output"]})
            return JsonResponse({
                "error": result["error"],
                "test_results": [{
                    "test_name": "Code Execution",
                    "passed": False,
                    "error": result["error"]
                }]
            })

        # Get problem and test cases
        try:
            problem = Problem.objects.get(id=problem_id)
            test_cases = problem.test_cases
        except Problem.DoesNotExist:
            return JsonResponse({"error": "Problem not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        # Run test cases
        test_results = []
        all_tests_passed = True

        for test_name, test_data in test_cases.items():
            result = run_code_with_test(user_code, test_data.get("input", ""))

            if result["success"]:
                passed = compare_outputs(test_data.get("output", ""), result["output"])
                if not passed:
                    all_tests_passed = False
                
                test_results.append({
                    "test_name": test_name,
                    "passed": passed,
                    "expected_output": test_data.get("output", ""),
                    "actual_output": result["output"]
                })
            else:
                all_tests_passed = False
                test_results.append({
                    "test_name": test_name,
                    "passed": False,
                    "error": result["error"]
                })

        # Check if problem was previously completed
        was_completed_before = UserProgress.objects.filter(
            user=request.user,
            problem=problem,
            is_completed=True
        ).exists()

        # Create submission and update progress
        submission = create_submission(request.user, problem, user_code, all_tests_passed)
        update_user_progress(request.user, problem, time_spent, all_tests_passed)

        # Update gamification elements if all tests passed
        if all_tests_passed:
            update_leaderboard(request.user, problem, was_completed_before)
            update_streak(request.user)

        return JsonResponse({
            "all_tests_passed": all_tests_passed,
            "test_results": test_results,
            "submission_id": submission.id
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
