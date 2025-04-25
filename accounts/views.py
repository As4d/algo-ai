from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
import json
from django.utils import timezone

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm
from .models import Profile


@ensure_csrf_cookie
@require_http_methods(['GET'])
def set_csrf_token(request):
    """
    We set the CSRF cookie on the frontend.
    """
    return JsonResponse({'message': 'CSRF cookie set'})


@require_http_methods(['POST'])
def login_view(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data['email']
        password = data['password']
    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'message': 'Invalid JSON'}, status=400
        )

    user = authenticate(request, username=email, password=password)

    if user:
        login(request, user)
        return JsonResponse({'success': True})
    return JsonResponse(
        {'success': False, 'message': 'Invalid credentials'}, status=401
    )


def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logged out'})


@require_http_methods(['GET'])
def user(request):
    if request.user.is_authenticated:
        return JsonResponse(
            {'username': request.user.username, 'email': request.user.email}
        )
    return JsonResponse(
        {'message': 'Not logged in'}, status=401
    )


@require_http_methods(['POST'])
def register(request):
    data = json.loads(request.body.decode('utf-8'))
    form = CreateUserForm(data)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': 'User registered successfully'}, status=201)
    else:
        errors = form.errors.as_json()
        return JsonResponse({'error': errors}, status=400)


@require_http_methods(['GET'])
def get_profile(request):
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

