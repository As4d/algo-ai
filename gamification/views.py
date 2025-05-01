from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.utils import timezone

from .models import LeaderboardEntry


@require_http_methods(["GET"])
def get_leaderboard(request):
    """
    Returns the current leaderboard, sorted by total problems solved.
    
    Args:
        request (HttpRequest): The HTTP request object.
        
    Returns:
        JsonResponse: A JSON response containing:
            - entries (list): List of leaderboard entries, each containing:
                - user__username (str): Username of the user
                - total_solved (int): Total number of problems solved
                - last_updated (datetime): Last update timestamp
    """
    entries = LeaderboardEntry.objects.order_by('-total_solved')[:50]
    
    return JsonResponse({
        'entries': list(entries.values(
            'user__username',
            'total_solved',
            'last_updated'
        ))
    })


@require_http_methods(["GET"])
@login_required
def get_user_stats(request):
    """
    Returns the current user's leaderboard stats.
    
    Args:
        request (HttpRequest): The HTTP request object containing the authenticated user.
        
    Returns:
        JsonResponse: A JSON response containing:
            - total_solved (int): Total number of problems solved by the user
            - last_updated (datetime): Last update timestamp, or None if no entry exists
    """
    try:
        entry = LeaderboardEntry.objects.get(user=request.user)
        return JsonResponse({
            'total_solved': entry.total_solved,
            'last_updated': entry.last_updated
        })
    except LeaderboardEntry.DoesNotExist:
        return JsonResponse({
            'total_solved': 0,
            'last_updated': None
        })
