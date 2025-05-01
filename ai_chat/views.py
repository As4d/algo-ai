import json
import requests
import os
import html
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.models import Profile
from django.core.exceptions import ObjectDoesNotExist
from problems.models import Problem

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = ""
SITE_NAME = ""

# Load problem type prompts
with open(os.path.join(os.path.dirname(__file__), 'prompt_building_blocks', 'problem_type_prompts.json'), 'r') as f:
    PROBLEM_TYPE_PROMPTS = json.load(f)

# Load experience guidance
with open(os.path.join(os.path.dirname(__file__), 'prompt_building_blocks', 'experience_guidance.json'), 'r') as f:
    EXPERIENCE_GUIDANCE = json.load(f)

def sanitise_code(code):
    """
    Sanitise user code to prevent XSS and other injection attacks.
    
    Args:
        code (str): The user's code to sanitise
        
    Returns:
        str: Sanitised code
    """
    # Remove any HTML tags
    code = re.sub(r'<[^>]+>', '', code)
    # Escape HTML special characters
    code = html.escape(code)
    # Remove any potential command injection attempts
    code = re.sub(r'[;&|`]', '', code)
    return code

def sanitise_text(text):
    """
    Sanitise text input to prevent XSS attacks.
    
    Args:
        text (str): The text to sanitise
        
    Returns:
        str: Sanitised text
    """
    # Remove any HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Escape HTML special characters
    text = html.escape(text)
    return text

def get_problem_type_prompt(problem_id):
    """
    Get the problem type specific prompt based on the problem ID.
    
    Args:
        problem_id (int): The ID of the problem
        
    Returns:
        str: The formatted problem type specific prompt, or empty string if no matching prompt
    """
    if not problem_id:
        return ""
        
    try:
        problem = Problem.objects.get(id=problem_id)
        problem_type = problem.problem_type
        if problem_type in PROBLEM_TYPE_PROMPTS:
            return f"""
            **Problem Type Specific Guidance:**
            {PROBLEM_TYPE_PROMPTS[problem_type]['hint_guidance']}
            
            {PROBLEM_TYPE_PROMPTS[problem_type]['additional_context']}
            """
    except Problem.DoesNotExist:
        pass
        
    return ""

def get_experience_guidance(experience_level):
    """
    Get the experience level specific guidance.
    
    Args:
        experience_level (str): The user's experience level (beginner, intermediate, or advanced)
        
    Returns:
        str: The formatted experience level guidance
    """
    if experience_level not in EXPERIENCE_GUIDANCE:
        return ""
        
    return f"""
    {EXPERIENCE_GUIDANCE[experience_level]['guidance']}
    
    {EXPERIENCE_GUIDANCE[experience_level]['context']}
    """

@csrf_exempt
def ai_chat(request):
    """Handle AI chat interactions using OpenRouter's DeepSeek R1 API."""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    try:
        data = json.loads(request.body.decode("utf-8"))
        user_code = sanitise_code(data.get("code", "").strip())
        terminal_output = sanitise_text(data.get("terminal", "").strip())
        problem_description = sanitise_text(data.get("question", "").strip())
        problem_id = data.get("problem_id")

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

        # Get problem type specific prompt
        problem_type_prompt = get_problem_type_prompt(problem_id)
        
        # Get experience level guidance
        experience_guidance = get_experience_guidance(experience_level)

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

        {experience_guidance}

        {problem_type_prompt}

        **General Guidance Protocol:**
        1. First, analyse the code and identify key issues or areas for improvement
        2. Instead of providing solutions:
           - Ask leading questions
           - Point out specific areas to think about
           - Provide small hints about concepts they should consider
        3. If the code is on the right track:
           - Suggest optimisations through questions
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
        2. Guide them to analyse test failures:
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
        4. Optimisation Suggestions (if applicable)
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
