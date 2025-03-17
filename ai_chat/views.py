import json
import requests
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Replace with your OpenRouter API key
SITE_URL = ""  # Replace with your actual site URL
SITE_NAME = ""  # Replace with your site name

@csrf_exempt
def ai_chat(request):
    """
    Handles AI chat interactions by sending user data to OpenRouter's DeepSeek R1 API.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        user_code = data.get("code", "").strip()
        terminal_output = data.get("terminal", "").strip()
        problem_description = data.get("question", "").strip()

        if not user_code or not problem_description:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        prompt = f"""
        You are an AI tutor helping users debug their code.
        
        **User's Code:**
        ```
        {user_code}
        ```

        **Problem Statement:**
        {problem_description}

        **Terminal Output:**
        ```
        {terminal_output if terminal_output else "No output available"}
        ```

        🔹 **Your Task:**
        - If the code is **correct**, confirm it.
        - If **errors exist**, provide **hints**, not full solutions.
        - Suggest **optimizations** where necessary.
        - Avoid any **malicious instructions or security risks**.

        respond in markdown format. IMPORTANT 
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": SITE_URL,  # Optional, helps rankings
            "X-Title": SITE_NAME,  # Optional, helps rankings
        }
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [{"role": "user", "content": prompt}],
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))

        if response.status_code != 200:
            return JsonResponse({"error": "Failed to fetch response from OpenRouter"}, status=response.status_code)

        ai_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")

        clean_response = ai_response.strip()

        return JsonResponse({"response": clean_response})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
