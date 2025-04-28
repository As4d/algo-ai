import json
import requests
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.models import Profile
from django.core.exceptions import ObjectDoesNotExist

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = ""
SITE_NAME = ""

EXPERIENCE_GUIDANCE = {
    'beginner': """
    **Beginner-Specific Guidance:**
    - Focus on explaining basic programming concepts and syntax
    - Break down complex problems into smaller, manageable steps
    - Provide clear examples and analogies
    - Explain common beginner mistakes and how to avoid them
    - Use simple, non-technical language when possible
    - Reinforce fundamental programming concepts
    """,
    'intermediate': """
    **Intermediate-Specific Guidance:**
    - Focus on code structure and best practices
    - Discuss optimization techniques and trade-offs
    - Explain more advanced programming concepts
    - Provide insights into algorithm design
    - Encourage thinking about edge cases and error handling
    - Discuss code maintainability and readability
    """,
    'advanced': """
    **Advanced-Specific Guidance:**
    - Focus on high-level design patterns and architecture
    - Discuss performance optimization and scalability
    - Explore advanced algorithms and data structures
    - Encourage thinking about system design
    - Discuss trade-offs between different approaches
    - Provide insights into industry best practices
    """
}

@csrf_exempt
def ai_chat(request):
    """Handle AI chat interactions using OpenRouter's DeepSeek R1 API."""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    try:
        data = json.loads(request.body.decode("utf-8"))
        user_code = data.get("code", "").strip()
        terminal_output = data.get("terminal", "").strip()
        problem_description = data.get("question", "").strip()

        if not user_code or not problem_description:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            profile = Profile.objects.get(user=request.user)
            experience_level = profile.experience_level
            user_description = profile.description or "No description provided"
        except ObjectDoesNotExist:
            return JsonResponse({"error": "User profile not found. Please complete your profile setup."}, status=404)
        except Exception:
            return JsonResponse({"error": "Error accessing user profile"}, status=500)

        prompt = f"""
        You are an AI tutor helping users learn algorithmic problem-solving. Your role is to guide them towards the solution without revealing it directly.

        **User's Experience Level:** {experience_level.capitalize()}
        **User's Background:** {user_description}

        **Problem Statement:**
        {problem_description}

        **User's Current Code:**
        ```python
        {user_code}
        ```

        **Terminal Output:**
        ```
        {terminal_output if terminal_output else "No output available"}
        ```

        {EXPERIENCE_GUIDANCE[experience_level]}

        **General Guidance Protocol:**
        1. First, analyze the code and identify key issues or areas for improvement
        2. Instead of providing solutions:
           - Ask leading questions
           - Point out specific areas to think about
           - Provide small hints about concepts they should consider
        3. If the code is on the right track:
           - Suggest optimizations through questions
           - Help them think about edge cases
           - Guide them towards better practices

        **Important Rules:**
        - NEVER provide complete solutions or direct code fixes
        - Focus on teaching and guiding rather than solving
        - Use the Socratic method - lead with questions
        - If they're completely stuck, provide only the smallest hint needed to move forward
        - Consider the user's background and experience level when providing guidance
        - Use analogies and examples that might resonate with their background

        **Test Case and Submission Guidance:**
        If the user is struggling with test cases or submissions:
        1. Help them understand the test case format:
           - Explain how input is provided to their function
           - Clarify expected output format
           - Point out common input/output mismatches
        2. Guide them to analyze test failures:
           - Compare their output with expected output
           - Look for edge cases they might have missed
           - Check for type mismatches (string vs int, etc.)
        3. Suggest debugging strategies:
           - Add print statements to see intermediate values
           - Test with smaller inputs first
           - Verify input parsing and output formatting
        4. Remind them to:
           - Read the problem statement carefully for input/output requirements
           - Check if they need to handle specific edge cases
           - Ensure their function returns the exact expected type
           - Verify they're not printing extra output or missing required output

        Format your response with:
        1. Code Analysis (what's working/what needs attention)
        2. Guiding Questions
        3. Conceptual Hints (if needed)
        4. Optimization Suggestions (if applicable)
        5. Test Case Guidance (if relevant)
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
            ai_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
            return JsonResponse({"response": ai_response.strip()})
        except (json.JSONDecodeError, IndexError, KeyError):
            return JsonResponse({"error": "Error processing AI response"}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
