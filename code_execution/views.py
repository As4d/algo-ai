import io
import sys
import traceback
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from problems.models import Problem, UserProgress, Submission
from gamification.models import LeaderboardEntry

def run_code_with_test(code, test_input=""):
    """
    Run code with given test input and return the output.
    """
    output_buffer = io.StringIO()
    sys.stdout = output_buffer
    sys.stderr = output_buffer

    try:
        # Create a dictionary of safe built-in functions
        SAFE_BUILTINS = {
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
        }

        # If there's test input, simulate stdin
        if test_input:
            sys.stdin = io.StringIO(test_input)

        # Execute the code with restricted builtins
        exec(code, {"__builtins__": SAFE_BUILTINS}, {})
        
        output = output_buffer.getvalue()
        return {"success": True, "output": output.strip()}
    except Exception as e:
        return {"success": False, "error": traceback.format_exc()}
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if test_input:
            sys.stdin = sys.__stdin__

def compare_outputs(expected, actual):
    """
    Compare expected and actual outputs, ignoring whitespace differences.
    """
    expected = expected.strip().replace('\r\n', '\n')
    actual = actual.strip().replace('\r\n', '\n')
    return expected == actual

@csrf_exempt
def execute_code(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        user_code = data.get("code", "").strip()
        problem_id = data.get("problem_id")
        run_tests = data.get("run_tests", False)
        time_spent = data.get("time_spent", 0)  # New parameter for tracking time spent

        if not user_code:
            return JsonResponse({"error": "No code provided"}, status=400)

        # If just running code without tests
        if not run_tests:
            result = run_code_with_test(user_code)
            if result["success"]:
                return JsonResponse({"output": result["output"]})
            else:
                return JsonResponse({
                    "error": result["error"],
                    "test_results": [{
                        "test_name": "Code Execution",
                        "passed": False,
                        "error": result["error"]
                    }]
                })

        # If running with tests, get the problem and its test cases
        try:
            problem = Problem.objects.get(id=problem_id)
            test_cases = problem.test_cases
        except Problem.DoesNotExist:
            return JsonResponse({"error": "Problem not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        # Run each test case
        test_results = []
        all_tests_passed = True

        for test_name, test_data in test_cases.items():
            test_input = test_data.get("input", "")
            expected_output = test_data.get("output", "")

            # Run the test
            result = run_code_with_test(user_code, test_input)

            if result["success"]:
                output = result["output"]
                passed = compare_outputs(expected_output, output)
                if not passed:
                    all_tests_passed = False
                
                test_results.append({
                    "test_name": test_name,
                    "passed": passed,
                    "expected_output": expected_output,
                    "actual_output": output
                })
            else:
                all_tests_passed = False
                test_results.append({
                    "test_name": test_name,
                    "passed": False,
                    "error": result["error"]
                })

        # Create submission record
        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            code_submitted=user_code,
            status='completed' if all_tests_passed else 'attempted',
            language=problem.language,
            created_at=timezone.now()
        )

        # Update user progress
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
        user_progress.attempts += 1
        if time_spent > 0:
            user_progress.time_spent = time_spent
        if all_tests_passed:
            user_progress.is_completed = True
            user_progress.last_submitted = timezone.now()
        user_progress.save()

        # Update leaderboard if all tests passed
        if all_tests_passed:
            leaderboard_entry, created = LeaderboardEntry.objects.get_or_create(
                user=request.user,
                defaults={
                    'total_solved': 1
                }
            )
            
            if not created:
                # Only update if this is the first time solving this problem
                if not user_progress.is_completed:
                    leaderboard_entry.total_solved += 1
                    leaderboard_entry.save()
            else:
                # For new entries, we already set total_solved to 1
                leaderboard_entry.save()

        return JsonResponse({
            "all_tests_passed": all_tests_passed,
            "test_results": test_results,
            "submission_id": submission.id
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
