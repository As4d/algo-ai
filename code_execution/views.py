import io
import sys
import traceback
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from problems.models import Problem

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

        if not user_code:
            return JsonResponse({"error": "No code provided"}, status=400)

        # If just running code without tests
        if not run_tests:
            result = run_code_with_test(user_code)
            if result["success"]:
                return JsonResponse({"output": result["output"]})
            else:
                return JsonResponse({"error": result["error"]}, status=400)

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

        return JsonResponse({
            "all_tests_passed": all_tests_passed,
            "test_results": test_results
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
