from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.utils import timezone
from datetime import timedelta

from .models import LeaderboardEntry


@require_http_methods(["GET"])
def get_leaderboard(request):
    """
    Returns the current leaderboard, sorted by weekly score or total solved based on query parameter.
    """
    sort_by = request.GET.get('sort', 'weekly')  # 'weekly' or 'total'
    
    if sort_by == 'weekly':
        # Only show entries updated in the last week
        week_ago = timezone.now().date() - timedelta(days=7)
        entries = LeaderboardEntry.objects.filter(
            last_updated__gte=week_ago
        ).order_by('-score_weekly', '-total_solved')[:50]
        
        return JsonResponse({
            'type': 'weekly',
            'entries': list(entries.values(
                'user__username',
                'score_weekly',
                'total_solved',
                'last_updated'
            ))
        })
    else:
        # Show all-time leaderboard
        entries = LeaderboardEntry.objects.order_by(
            '-total_solved', '-score_weekly'
        )[:50]
        
        return JsonResponse({
            'type': 'total',
            'entries': list(entries.values(
                'user__username',
                'score_weekly',
                'total_solved',
                'last_updated'
            ))
        })


@require_http_methods(["GET"])
@login_required
def get_user_stats(request):
    """
    Returns the current user's leaderboard stats.
    """
    entry, created = LeaderboardEntry.objects.get_or_create(
        user=request.user,
        defaults={
            'total_solved': 0,
            'score_weekly': 0
        }
    )
    
    return JsonResponse({
        'total_solved': entry.total_solved,
        'score_weekly': entry.score_weekly,
        'last_updated': entry.last_updated
    })
