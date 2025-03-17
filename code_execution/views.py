import io
import sys
import traceback
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Disable CSRF for local testing (secure it later)
def execute_code(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_code = data.get("code", "").strip()

            if not user_code:
                return JsonResponse({"error": "No code provided"}, status=400)

            # Capture stdout and stderr
            output_buffer = io.StringIO()
            sys.stdout = output_buffer
            sys.stderr = output_buffer

            try:
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
                }

                exec(user_code, {"__builtins__": SAFE_BUILTINS}, {})

                output = output_buffer.getvalue()
            except Exception as e:
                output = traceback.format_exc()  # Capture error traceback
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

            return JsonResponse({"output": output.strip()})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)
