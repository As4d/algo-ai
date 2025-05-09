"""
User authentication and profile management views.

This module provides functionality to:
- Handle user authentication (login, logout, registration)
- Manage user profiles and settings
- Handle password changes
- Provide CSRF protection for frontend
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
import json
from django.utils import timezone
from django.contrib.auth.models import User

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm
from .models import Profile


@ensure_csrf_cookie
@require_http_methods(['GET'])
def set_csrf_token(request):
    """
    Set CSRF token cookie for frontend authentication.
    
    Returns:
        JsonResponse: Success message indicating CSRF cookie was set
    """
    return JsonResponse({'message': 'CSRF cookie set'})


@require_http_methods(['POST'])
def login_view(request):
    """
    Handle user login authentication.
    
    Args:
        request: HTTP request containing email and password
        
    Returns:
        JsonResponse: Success status and message
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data['email']
        password = data['password']
    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'message': 'Invalid JSON'}, status=400
        )

    try:
        # Get user by email
        user = User.objects.get(email=email)
        # Authenticate with username and password
        auth_user = authenticate(request, username=user.username, password=password)
        
        if auth_user:
            login(request, auth_user)
            return JsonResponse({'success': True})
        return JsonResponse(
            {'success': False, 'message': 'Invalid credentials'}, status=401
        )
    except User.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': 'Invalid credentials'}, status=401
        )


@csrf_protect
@require_http_methods(['POST'])
def logout_view(request):
    """
    Handle user logout and session cleanup.
    
    Returns:
        JsonResponse: Success message and cleared session cookie
    """
    logout(request)
    response = JsonResponse({'message': 'Logged out'})
    response.delete_cookie('sessionid')  # Only delete session cookie
    return response


@require_http_methods(['GET'])
def user(request):
    """
    Get current authenticated user information.
    
    Returns:
        JsonResponse: User details if authenticated, error message otherwise
    """
    if request.user.is_authenticated:
        return JsonResponse(
            {'username': request.user.username, 'email': request.user.email}
        )
    return JsonResponse(
        {'message': 'Not logged in'}, status=401
    )


@require_http_methods(['POST'])
def register(request):
    """
    Handle new user registration.
    
    Args:
        request: HTTP request containing user registration data
        
    Returns:
        JsonResponse: Success message or form validation errors
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        form = CreateUserForm(data)
        
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'User registered successfully'}, status=201)
        return JsonResponse({'error': form.errors.as_json()}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@require_http_methods(['GET'])
def get_profile(request):
    """
    Retrieve user profile information.
    
    Returns:
        JsonResponse: Complete profile data or error message
    """
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Not logged in'}, status=401)
    
    try:
        profile = Profile.objects.get(user=request.user)
        return JsonResponse({
            'username': request.user.username,
            'email': request.user.email,
            'experience_level': profile.experience_level,
            'description': profile.description,
            'streak': profile.streak,
            'high_score_streak': profile.high_score_streak,
            'password_last_changed': profile.password_last_changed,
            'date_joined': request.user.date_joined
        })
    except Profile.DoesNotExist:
        return JsonResponse({'message': 'Profile not found'}, status=404)


@require_http_methods(['PUT'])
def update_profile(request):
    """
    Update user profile information.
    
    Args:
        request: HTTP request containing profile update data
        
    Returns:
        JsonResponse: Updated profile data or error message
    """
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Not logged in'}, status=401)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        profile = Profile.objects.get(user=request.user)
        
        # Update allowed fields
        if 'experience_level' in data:
            profile.experience_level = data['experience_level']
        if 'description' in data:
            profile.description = data['description']
            
        profile.save()
        return JsonResponse({
            'message': 'Profile updated successfully',
            'experience_level': profile.experience_level,
            'description': profile.description
        })
    except Profile.DoesNotExist:
        return JsonResponse({'message': 'Profile not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)


@require_http_methods(['PUT'])
def change_password(request):
    """
    Handle user password change request.
    
    Args:
        request: HTTP request containing current and new password
        
    Returns:
        JsonResponse: Success message or error details
    """
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Not logged in'}, status=401)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Verify current password
        if not request.user.check_password(current_password):
            return JsonResponse({'message': 'Current password is incorrect'}, status=400)
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        # Update password change date in profile
        profile = Profile.objects.get(user=request.user)
        profile.password_last_changed = timezone.now()
        profile.save()
        
        return JsonResponse({'message': 'Password updated successfully'})
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)
